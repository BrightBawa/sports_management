import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Teams"
    context.teams = frappe.get_all(
        "Sports Team",
        filters={"show_on_website": 1, "profile_status": "Published"},
        fields=["team_name", "route", "season", "sport", "campus"],
        order_by="team_name asc",
    )
    return context
