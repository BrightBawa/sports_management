import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Athletes"
    context.athletes = frappe.get_all(
        "Athlete Profile",
        filters={"publish_athlete_profile": 1, "profile_status": "Published"},
        fields=["public_name", "route", "primary_sport", "current_team"],
        order_by="public_name asc",
    )
    return context
