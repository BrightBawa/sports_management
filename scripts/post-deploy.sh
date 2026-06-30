#!/usr/bin/env bash

set -euo pipefail

usage() {
	cat <<'EOF'
Usage: ./scripts/post-deploy.sh --site <site> [options]

Post-deploy refresh for this bench. It runs the site update commands and then
recycles the preloaded gunicorn web master so newly linked apps are visible to
fresh workers even when `bench restart` is not available from the current shell.

Options:
  --site <site>        Site name to migrate, clear, and health-check.
  --skip-migrate       Skip `bench migrate` and only clear cache + recycle web.
  --timeout <seconds>  Seconds to wait for a new web master and health check.
                       Default: 90
  --check-path <path>  Health-check path served by gunicorn. Default: /api/method/ping
  -h, --help           Show this help text.
EOF
}

require_command() {
	local command_name="$1"
	if ! command -v "$command_name" >/dev/null 2>&1; then
		echo "Missing required command: $command_name" >&2
		exit 1
	fi
}

bench_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
site=""
skip_migrate=0
timeout_seconds=90
check_path="/api/method/ping"

while (($#)); do
	case "$1" in
	--site)
		site="${2:-}"
		shift 2
		;;
	--skip-migrate)
		skip_migrate=1
		shift
		;;
	--timeout)
		timeout_seconds="${2:-}"
		shift 2
		;;
	--check-path)
		check_path="${2:-}"
		shift 2
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		echo "Unknown argument: $1" >&2
		usage >&2
		exit 1
		;;
	esac
done

if [[ -z "$site" ]]; then
	echo "Error: --site is required." >&2
	usage >&2
	exit 1
fi

if [[ ! "$timeout_seconds" =~ ^[0-9]+$ ]] || ((timeout_seconds < 1)); then
	echo "Error: --timeout must be a positive integer." >&2
	exit 1
fi

cd "$bench_root"

if [[ ! -f "Procfile" ]] || [[ ! -d "env" ]] || [[ ! -d "sites" ]]; then
	echo "Error: $bench_root does not look like a bench root." >&2
	exit 1
fi

require_command bench
require_command curl
require_command pgrep
require_command awk

run_bench() {
	bench --site "$site" "$@"
}

get_supervisor_web_program() {
	if [[ ! -f "$bench_root/config/supervisor.conf" ]]; then
		return 1
	fi

	awk -F'[][]' '
		/^\[program:.*frappe-web\]$/ {
			name = $2
			sub(/^program:/, "", name)
			print name
			exit
		}
	' "$bench_root/config/supervisor.conf"
}

restart_via_supervisorctl() {
	local program_name

	if ! command -v supervisorctl >/dev/null 2>&1; then
		return 1
	fi

	program_name="$(get_supervisor_web_program || true)"
	if [[ -z "$program_name" ]]; then
		return 1
	fi

	if supervisorctl restart "$program_name" >/dev/null 2>&1; then
		echo "Restarted web via supervisorctl program $program_name."
		return 0
	fi

	return 1
}

get_gunicorn_master_pid() {
	pgrep -fo "${bench_root}/env/bin/gunicorn .*frappe\\.app:application --preload" || true
}

wait_for_new_master_pid() {
	local old_pid="$1"
	local deadline=$((SECONDS + timeout_seconds))
	local new_pid

	while ((SECONDS < deadline)); do
		new_pid="$(get_gunicorn_master_pid)"
		if [[ -n "$new_pid" && "$new_pid" != "$old_pid" ]]; then
			printf '%s\n' "$new_pid"
			return 0
		fi
		sleep 1
	done

	return 1
}

recycle_gunicorn_master() {
	local old_pid
	local new_pid

	old_pid="$(get_gunicorn_master_pid)"
	if [[ -z "$old_pid" ]]; then
		echo "No preloaded gunicorn master detected for this bench. Skipping web recycle."
		return 0
	fi

	echo "Recycling preloaded gunicorn master PID $old_pid."
	kill -TERM "$old_pid"

	new_pid="$(wait_for_new_master_pid "$old_pid")" || {
		echo "Timed out waiting for a new gunicorn master." >&2
		return 1
	}

	echo "New gunicorn master PID $new_pid is up."
}

wait_for_site_health() {
	local deadline=$((SECONDS + timeout_seconds))

	echo "Waiting for http://127.0.0.1:8000${check_path} on host ${site}."
	while ((SECONDS < deadline)); do
		if curl -fsS -o /dev/null -H "Host: ${site}" "http://127.0.0.1:8000${check_path}" >/dev/null 2>&1; then
			echo "Health check passed for ${site}."
			return 0
		fi
		sleep 2
	done

	echo "Timed out waiting for ${site} to pass the local gunicorn health check." >&2
	return 1
}

if ((skip_migrate == 0)); then
	echo "Running bench migrate for ${site}."
	run_bench migrate
else
	echo "Skipping bench migrate for ${site}."
fi

echo "Clearing cache for ${site}."
run_bench clear-cache

if ! restart_via_supervisorctl; then
	recycle_gunicorn_master
fi

wait_for_site_health

echo "Post-deploy refresh completed for ${site}."
