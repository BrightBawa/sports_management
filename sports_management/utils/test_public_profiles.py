import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import frappe

from sports_management.sports.doctype.sports_team.sports_team import SportsTeam
from sports_management.utils.public_profiles import (
    PUBLIC_DETAILS,
    get_public_details,
    get_public_image_url,
    get_published_profile,
    validate_optional_public_photo,
)


class TestPublicProfileOptions(unittest.TestCase):
    def setUp(self):
        self.translation = patch("sports_management.utils.public_profiles._", side_effect=lambda s: s)
        self.translation.start()
        self.addCleanup(self.translation.stop)

    def test_optional_values_require_their_checkbox(self):
        for doctype, fields in PUBLIC_DETAILS.items():
            for fieldname, label in fields:
                with self.subTest(doctype=doctype, field=fieldname):
                    doc = frappe._dict(doctype=doctype, **{fieldname: "Available internally"})
                    self.assertEqual(get_public_details(doc), [])
                    doc[f"show_{fieldname}"] = 1
                    self.assertEqual(get_public_details(doc)[0].value, "Available internally")
                    doc[f"show_{fieldname}"] = 0
                    self.assertEqual(get_public_details(doc), [])

    def test_empty_and_whitespace_values_do_not_create_sections(self):
        for value in (None, "", "   "):
            doc = frappe._dict(doctype="Coach Profile", show_experience=1, experience=value)
            self.assertEqual(get_public_details(doc), [])

    def test_unknown_fields_cannot_be_made_public(self):
        doc = frappe._dict(doctype="Athlete Profile", student="INTERNAL-STUDENT", show_student=1)
        self.assertEqual(get_public_details(doc), [])

    def test_string_zero_checkbox_is_false(self):
        doc = frappe._dict(doctype="Coach Profile", show_experience="0", experience="Hidden")
        self.assertEqual(get_public_details(doc), [])

    def test_only_public_image_urls_are_rendered(self):
        for value in (
            "/private/files/photo.jpg", "/%70rivate/files/photo.jpg",
            "https://school.example/private/files/photo.jpg", "javascript:alert(1)",
            "https://[invalid", None,
        ):
            with self.subTest(value=value):
                self.assertIsNone(get_public_image_url(value))
        for value in ("/files/photo.jpg", "/assets/sports_management/photo.jpg", "https://school.example/photo.jpg"):
            self.assertEqual(get_public_image_url(value), value)

    def test_optional_private_photo_is_rejected_only_when_enabled_and_published(self):
        values = {"public_photo": "/private/files/photo.jpg", "show_public_photo": 0}
        doc = SimpleNamespace(
            get=values.get, is_website_published=lambda: True,
            meta=SimpleNamespace(get_label=lambda field: "Public Photo"),
        )
        validate_optional_public_photo(doc, "public_photo")
        values["show_public_photo"] = 1
        with patch("sports_management.utils.public_profiles.frappe.throw", side_effect=frappe.ValidationError):
            with self.assertRaises(frappe.ValidationError):
                validate_optional_public_photo(doc, "public_photo")
        doc.is_website_published = lambda: False
        validate_optional_public_photo(doc, "public_photo")

    def test_related_profile_lookup_requires_publication(self):
        db = MagicMock()
        with patch("sports_management.utils.public_profiles.frappe.db", new=db):
            get_published_profile("Coach Profile", "Coach", ["coach_name", "route"])
            filters = db.get_value.call_args.args[1]
            self.assertEqual(filters, {"name":"Coach", "publish_coach_profile":1, "profile_status":"Published"})

    def test_hidden_team_roster_and_staff_are_not_queried(self):
        doc = frappe._dict(doctype="Sports Team", name="Team", team_name="Team", sport="Football",
                           head_coach="Private Coach", team_captain="Private Captain")
        with patch("sports_management.sports.doctype.sports_team.sports_team.get_published_profile", return_value=None) as linked:
            with patch("sports_management.sports.doctype.sports_team.sports_team.frappe.get_all") as get_all:
                context = SportsTeam.get_context(doc, frappe._dict())
                self.assertEqual(context.public_details, [])
                self.assertEqual(context.athletes, [])
                self.assertEqual(linked.call_count, 1)  # Only the sport, whose association is public.
                get_all.assert_not_called()
