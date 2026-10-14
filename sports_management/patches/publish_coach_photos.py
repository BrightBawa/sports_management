from pathlib import PurePosixPath

import frappe


def execute():
    """Copy published coaches' private photos without changing shared staff files."""
    coaches = frappe.get_all(
        "Coach Profile",
        filters={
            "publish_coach_profile": 1,
            "profile_status": "Published",
            "public_photo": ["like", "/private/files/%"],
        },
        fields=["name", "slug", "public_photo", "route"],
    )
    updated = []
    for coach in coaches:
        source_name = frappe.db.get_value(
            "File",
            {
                "file_url": coach.public_photo,
                "attached_to_doctype": "Coach Profile",
                "attached_to_name": coach.name,
                "attached_to_field": "public_photo",
                "is_private": 1,
            },
            "name",
        )
        if not source_name:
            frappe.throw(f"Public Photo attachment missing for Coach Profile {coach.name}")

        source = frappe.get_doc("File", source_name)
        photo = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": f"coach-{coach.slug or frappe.generate_hash(length=8)}{PurePosixPath(source.file_name).suffix}",
                "content": source.get_content(encodings=[]),
                "is_private": 0,
                "attached_to_doctype": "Coach Profile",
                "attached_to_name": coach.name,
                "attached_to_field": "public_photo",
            }
        ).insert(ignore_permissions=True)
        frappe.db.set_value("Coach Profile", coach.name, "public_photo", photo.file_url)
        frappe.clear_document_cache("Coach Profile", coach.name)
        updated.append(coach.name)

    if updated:
        from frappe.website.utils import clear_website_cache

        clear_website_cache()

    return updated
