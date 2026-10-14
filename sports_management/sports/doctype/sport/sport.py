import frappe

from sports_management.utils.document_helpers import (
    make_unique_name,
    set_route,
    set_unique_slug,
    sync_published_on,
    validate_required_fields_for_publication,
)
from sports_management.website_context import PublicWebsiteGenerator


class Sport(PublicWebsiteGenerator):
    website = frappe._dict(
        page_title_field="sport_name",
        condition_field="show_on_website",
        template="templates/generators/sport.html",
        no_cache=1,
    )
    website_publish_field = "show_on_website"
    website_status_field = ""

    def autoname(self):
        self.name = make_unique_name(self.doctype, self.sport_name, self.name)

    def validate(self):
        set_unique_slug(self, self.sport_name)
        set_route(self, f"sports/{self.slug}")
        sync_published_on(self, "show_on_website", status_field="")
        validate_required_fields_for_publication(
            self,
            "show_on_website",
            status_field="",
            required_fields=("route",),
            require_one_of=("description",),
        )

        if not self.is_active and self.show_on_website:
            frappe.throw("Inactive sports cannot be published on the website.")

    def website_extra_public_check(self) -> bool:
        return bool(self.is_active)

    def get_context(self, context):
        context.no_cache = 1
        context.title = self.sport_name
        context.parents = [{"name": "Sports", "route": "/sports"}]
        context.teams = frappe.get_all(
            "Sports Team",
            filters={"sport": self.name, "show_on_website": 1, "profile_status": "Published"},
            fields=["team_name", "route", "season", "age_group", "gender_category", "show_age_group", "show_gender_category"],
            order_by="team_name asc",
        )
        return context
