from urllib.parse import unquote, urlsplit

import frappe
from frappe import _
from frappe.utils import cint


# Only these optional fields can become public, and each requires its own checkbox.
PUBLIC_DETAILS = {
    "Coach Profile": (
        ("qualifications", "Professional qualifications"),
        ("experience", "Coaching experience"),
        ("coaching_philosophy", "Coaching philosophy"),
        ("achievements_summary", "Coaching achievements"),
        ("languages", "Languages"),
    ),
    "Athlete Profile": (
        ("jersey_number", "Jersey number"),
        ("achievements_summary", "Achievements"),
        ("athletic_strengths", "Athletic strengths"),
        ("sporting_goals", "Sporting goals"),
        ("dominant_side", "Dominant hand / foot"),
    ),
    "Sports Team": (
        ("team_motto", "Team motto"),
        ("team_level", "Team level"),
        ("age_group", "Age group"),
        ("gender_category", "Gender category"),
        ("campus", "Campus"),
        ("achievements_summary", "Team achievements"),
        ("training_venue", "Training venue"),
        ("training_schedule", "Training schedule"),
    ),
}


def get_public_details(doc):
    details = []
    for fieldname, label in PUBLIC_DETAILS.get(doc.doctype, ()):
        value = doc.get(fieldname)
        if cint(doc.get(f"show_{fieldname}")) and value and str(value).strip():
            details.append(frappe._dict(label=_(label), value=value, route=None))
    return details


def get_public_image_url(value):
    if not value:
        return None
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    path = unquote(parts.path)
    if path.startswith("/private/"):
        return None
    if (parts.scheme in ("http", "https") and parts.netloc) or (
        not parts.scheme and not parts.netloc and path.startswith(("/files/", "/assets/"))
    ):
        return value
    return None


def validate_optional_public_photo(doc, fieldname):
    value = doc.get(fieldname)
    if doc.is_website_published() and cint(doc.get(f"show_{fieldname}")) and value:
        if not get_public_image_url(value):
            frappe.throw(
                _("{0} must be a public image to display on the website. Upload a public image or untick its display option.").format(doc.meta.get_label(fieldname))
            )


def get_published_profile(doctype, name, fields):
    if not name:
        return None
    flags = {
        "Coach Profile": {"publish_coach_profile": 1, "profile_status": "Published"},
        "Athlete Profile": {"publish_athlete_profile": 1, "profile_status": "Published"},
        "Sports Team": {"show_on_website": 1, "profile_status": "Published"},
        "Sport": {"show_on_website": 1, "is_active": 1},
    }
    return frappe.db.get_value(doctype, {"name": name, **flags[doctype]}, fields, as_dict=True)
