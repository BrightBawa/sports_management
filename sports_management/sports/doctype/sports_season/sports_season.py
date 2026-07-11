import frappe
from frappe import _
from frappe.model.document import Document

from sports_management.utils.document_helpers import make_unique_name, validate_date_range


class SportsSeason(Document):
    def autoname(self):
        self.name = make_unique_name(self.doctype, self.season_name, self.name)

    def validate(self):
        validate_date_range(self, "start_date", "end_date", _("Sports season"))
        self.validate_current_season()

    def validate_current_season(self):
        if not self.is_current:
            return

        existing = frappe.get_all(
            "Sports Season",
            filters=[["is_current", "=", 1], ["name", "!=", self.name]],
            limit=1,
            pluck="name",
        )
        if existing:
            frappe.throw(_("Only one Sports Season can be marked as current."))
