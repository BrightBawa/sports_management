import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Sports"
    context.sports = frappe.get_all(
        "Sport",
        filters={"show_on_website": 1, "is_active": 1},
        fields=["sport_name", "description", "route", "category"],
        order_by="sport_name asc",
    )
    return context
