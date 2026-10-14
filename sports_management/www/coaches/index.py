import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Coaches"
    context.coaches = frappe.get_all(
        "Coach Profile",
        filters={"publish_coach_profile": 1, "profile_status": "Published"},
        fields=["coach_name", "route", "coaching_role", "sport_specialties", "public_photo"],
        order_by="coach_name asc",
    )
    return context
