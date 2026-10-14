# Copyright (c) 2026, GCIHS and Contributors
# See license.txt

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import frappe

from sports_management.sports.doctype.coach_profile.coach_profile import CoachProfile


class TestCoachPhotoPublication(unittest.TestCase):
    def validate_photo(self, photo, published=True):
        doc = SimpleNamespace(public_photo=photo, is_website_published=lambda: published)
        CoachProfile.validate_public_photo(doc)

    def test_published_private_photos_are_rejected(self):
        for photo in (
            "/private/files/coach.jpg",
            "https://school.example/private/files/coach.jpg",
            "/%70rivate/files/coach.jpg",
        ):
            with self.subTest(photo=photo), patch(
                "sports_management.sports.doctype.coach_profile.coach_profile._", side_effect=lambda s: s
            ), patch(
                "sports_management.sports.doctype.coach_profile.coach_profile.frappe.throw",
                side_effect=frappe.ValidationError,
            ), self.assertRaises(frappe.ValidationError):
                self.validate_photo(photo)

    def test_public_photos_are_allowed(self):
        for photo in ("/files/coach.jpg", "https://school.example/files/coach.jpg"):
            with self.subTest(photo=photo):
                self.validate_photo(photo)

    def test_drafts_can_keep_private_photos(self):
        self.validate_photo("/private/files/coach.jpg", published=False)

    def test_empty_photo_is_left_to_required_field_validation(self):
        self.validate_photo(None)
