# Deployment Refresh

Use `scripts/post-deploy.sh` after app installs, `bench migrate`, or any deploy that changes the installed app set.

Why this exists:
- This bench runs gunicorn with `--preload`.
- A plain worker reload is not enough when a new app has been linked into `env/site-packages`.
- `bench restart` may fail from an unprivileged shell because it shells out through `sudo supervisorctl`.

Recommended command:

```bash
cd /home/frapadmin/gcihs-bench
./scripts/post-deploy.sh --site portal.gcihs.edu.gh
```

If you already ran `bench migrate`, skip it in the helper:

```bash
cd /home/frapadmin/gcihs-bench
./scripts/post-deploy.sh --site portal.gcihs.edu.gh --skip-migrate
```

What the helper does:
- runs `bench --site <site> migrate` unless `--skip-migrate` is set
- runs `bench --site <site> clear-cache`
- tries a clean supervisor web restart when `supervisorctl` is usable
- otherwise recycles the preloaded gunicorn master directly and waits for a healthy local response
