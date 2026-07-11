import frappe

from sports_management.utils.document_helpers import (
    get_student_display_name,
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from sports_management.website_context import PublicWebsiteGenerator


class AthleteProfile(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="public_name",
        condition_field="publish_athlete_profile",
        template="templates/generators/athlete_profile.html",
        no_cache=1,
    )
    website_publish_field = "publish_athlete_profile"

    def autoname(self):
        self.public_name = self.public_name or get_student_display_name(self.student)
        self.name = make_unique_name(self.doctype, self.public_name or self.student, self.name)

    def validate(self):
        self.public_name = self.public_name or get_student_display_name(self.student)
        set_unique_slug(self, self.public_name or self.student)
        set_route(self, f"athletes/{self.slug}")
        sync_published_on(self, "publish_athlete_profile")
        validate_publication_state(self, "publish_athlete_profile")
        validate_required_fields_for_publication(
            self,
            "publish_athlete_profile",
            required_fields=("route", "public_photo"),
            require_one_of=("short_bio",),
        )

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.public_name
        context.parents = [{"name": "Athletes", "route": "/athletes"}]
        context.team_row = None
        if self.current_team:
            context.team_row = frappe.db.get_value(
                "Sports Team", self.current_team, ["team_name", "route"], as_dict=True
            )
        return context
