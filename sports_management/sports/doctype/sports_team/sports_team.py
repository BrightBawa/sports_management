import frappe

from sports_management.utils.document_helpers import (
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from sports_management.website_context import PublicWebsiteGenerator


class SportsTeam(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="team_name",
        condition_field="show_on_website",
        template="templates/generators/sports_team.html",
        no_cache=1,
    )
    website_publish_field = "show_on_website"

    def autoname(self):
        self.name = make_unique_name(self.doctype, self.team_name, self.name)

    def validate(self):
        set_unique_slug(self, self.team_name)
        set_route(self, f"teams/{self.slug}")
        sync_published_on(self, "show_on_website")
        validate_publication_state(self, "show_on_website")
        validate_required_fields_for_publication(
            self,
            "show_on_website",
            required_fields=("route",),
            require_one_of=("description", "training_schedule"),
        )

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.team_name
        context.parents = [{"name": "Sports", "route": "/sports"}]
        context.sport_row = frappe.db.get_value(
            "Sport", self.sport, ["sport_name", "route"], as_dict=True
        )
        context.athletes = frappe.get_all(
            "Athlete Profile",
            filters={
                "current_team": self.name,
                "publish_athlete_profile": 1,
                "profile_status": "Published",
            },
            fields=["public_name", "route", "preferred_position", "jersey_number"],
            order_by="public_name asc",
        )
        return context
