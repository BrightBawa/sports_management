import frappe


def execute():
    """Preserve previously displayed details while making additional fields opt-in."""
    for doctype, fieldnames in (
        ("Athlete Profile", ("show_preferred_position", "show_jersey_number", "show_current_team")),
        ("Sports Team", ("show_age_group", "show_gender_category", "show_athletes")),
    ):
        frappe.db.set_value(doctype, {}, dict.fromkeys(fieldnames, 1), update_modified=False)

    # Qualifications and experience were already shown on published coach profiles.
    # Draft content and all newly introduced details remain opt-in.
    for fieldname in ("qualifications", "experience"):
        for name in frappe.get_all(
            "Coach Profile",
            filters={
                "publish_coach_profile": 1,
                "profile_status": "Published",
                fieldname: ["is", "set"],
            },
            pluck="name",
        ):
            frappe.db.set_value("Coach Profile", name, f"show_{fieldname}", 1, update_modified=False)
