from frappe import _


def get_data():
    return [
        {
            "module_name": "Sports",
            "category": "Modules",
            "label": _("Sports"),
            "type": "module",
            "description": _("Teams, athletes, coaches, fixtures, results, and training."),
        }
    ]
