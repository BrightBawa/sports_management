import frappe


ROLE_NAMES = (
    "Sports Manager",
    "Sports Administrator",
    "Head Coach",
    "Assistant Coach",
    "Team Manager",
    "Sports Content Editor",
    "Sports Results Officer",
    "Sports Viewer",
)


def ensure_roles():
    for role_name in ROLE_NAMES:
        if frappe.db.exists("Role", role_name):
            continue
        frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
            ignore_permissions=True
        )


def setup_workspace():
    frappe.reload_doc("sports", "workspace", "sports")
    frappe.clear_cache()


def after_install():
    ensure_roles()
    setup_workspace()
    frappe.db.commit()


def after_migrate():
    ensure_roles()
    setup_workspace()
    frappe.db.commit()
