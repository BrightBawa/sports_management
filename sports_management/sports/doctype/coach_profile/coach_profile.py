from urllib.parse import unquote, urlsplit

import frappe
from frappe import _

from sports_management.utils.document_helpers import (
    get_employee_display_name,
    get_instructor_display_name,
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from sports_management.utils.public_profiles import get_public_details
from sports_management.website_context import PublicWebsiteGenerator


class CoachProfile(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="coach_name",
        condition_field="publish_coach_profile",
        template="templates/generators/coach_profile.html",
        no_cache=1,
    )
    website_publish_field = "publish_coach_profile"

    def autoname(self):
        self.coach_name = self.get_coach_name()
        self.name = make_unique_name(self.doctype, self.coach_name, self.name)

    def validate(self):
        self.validate_coach_type()
        self.coach_name = self.get_coach_name()
        set_unique_slug(self, self.coach_name)
        set_route(self, f"coaches/{self.slug}")
        sync_published_on(self, "publish_coach_profile")
        validate_publication_state(self, "publish_coach_profile")
        validate_required_fields_for_publication(
            self,
            "publish_coach_profile",
            required_fields=("route", "public_photo"),
            require_one_of=("biography", "sport_specialties"),
        )
        self.validate_public_photo()

    def validate_public_photo(self):
        if not self.is_website_published() or not self.public_photo:
            return

        photo_path = unquote(urlsplit(self.public_photo).path)
        if photo_path.startswith("/private/"):
            frappe.throw(
                _("Public Photo must be accessible to website visitors. Upload a public image before publishing.")
            )

    def get_coach_name(self) -> str:
        return (
            self.coach_name
            or get_employee_display_name(self.employee)
            or get_instructor_display_name(self.instructor)
            or _("Unnamed Coach")
        )

    def validate_coach_type(self):
        if self.coach_type == "Internal" and not (self.employee or self.instructor):
            frappe.throw(_("Internal coach profiles must link to an Employee or Instructor."))

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.coach_name
        context.parents = [{"name": "Coaches", "route": "/coaches"}]
        context.public_details = get_public_details(self)
        context.teams = frappe.get_all(
            "Sports Team",
            filters={
                "head_coach": self.name,
                "show_on_website": 1,
                "profile_status": "Published",
                "show_head_coach": 1,
            },
            fields=["team_name", "route", "season"],
            order_by="team_name asc",
        )
        return context
