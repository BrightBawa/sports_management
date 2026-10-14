import frappe

from sports_management.utils.document_helpers import (
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_publication_state,
    validate_required_fields_for_publication,
)
from sports_management.utils.public_profiles import (
    get_public_details,
    get_public_image_url,
    get_published_profile,
    validate_optional_public_photo,
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
        validate_optional_public_photo(self, "team_photo")

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.team_name
        context.parents = [{"name": "Sports", "route": "/sports"}]
        context.public_details = get_public_details(self)
        context.profile_photo = get_public_image_url(self.team_photo) if self.get("show_team_photo") else None
        context.sport_row = get_published_profile(
            "Sport", self.sport, ["sport_name", "route"]
        )
        for fieldname, doctype, title_field, label in (
            ("head_coach", "Coach Profile", "coach_name", "Head coach"),
            ("team_captain", "Athlete Profile", "public_name", "Team captain"),
        ):
            if self.get(f"show_{fieldname}") and self.get(fieldname):
                row = get_published_profile(doctype, self.get(fieldname), [title_field, "route"])
                if row:
                    context.public_details.append(
                        frappe._dict(label=frappe._(label), value=row[title_field], route=row.route)
                    )
        context.athletes = []
        if self.get("show_athletes"):
            context.athletes = frappe.get_all(
                "Athlete Profile",
                filters={
                    "current_team": self.name,
                    "publish_athlete_profile": 1,
                    "profile_status": "Published",
                    "show_current_team": 1,
                },
                fields=["public_name", "route", "preferred_position", "jersey_number", "show_preferred_position", "show_jersey_number"],
                order_by="public_name asc",
            )
        return context
