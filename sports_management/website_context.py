from __future__ import annotations

import frappe
from frappe.utils import cstr
from frappe.website.website_generator import WebsiteGenerator


class PublicWebsiteGenerator(WebsiteGenerator):
    website = frappe._dict(no_cache=1)
    website_publish_field = ""
    website_status_field = "profile_status"

    def website_extra_public_check(self) -> bool:
        return True

    def is_website_published(self):
        if self.website_publish_field and not self.get(self.website_publish_field):
            return False

        if self.website_status_field and self.get(self.website_status_field) != "Published":
            return False

        return self.website_extra_public_check()

    def has_website_permission(self, ptype, user, verbose=False):
        if user == "Guest":
            return self.is_website_published()

        return self.has_permission(ptype=ptype, user=user, verbose=verbose)


def get_query_value(key: str, default: str = "") -> str:
    return cstr(frappe.form_dict.get(key) or default).strip()


def add_filter(filters: dict, fieldname: str, value):
    if value:
        filters[fieldname] = value


def get_doc_map(
    doctype: str,
    names: list[str] | tuple[str, ...],
    fields: list[str],
    filters: dict | None = None,
) -> dict[str, frappe._dict]:
    unique_names = [name for name in dict.fromkeys(names) if name]
    if not unique_names:
        return {}

    query_fields = ["name"] + [fieldname for fieldname in fields if fieldname != "name"]
    doc_filters = {"name": ["in", unique_names]}
    if filters:
        doc_filters.update(filters)

    rows = frappe.get_all(doctype, fields=query_fields, filters=doc_filters)
    return {row.name: row for row in rows}
