#!/usr/bin/env python3
import os
import frappe

os.chdir('/home/frapadmin/gcihs-bench/sites')

def update_versions():
    frappe.init(site='portal.gcihs.edu.gh')
    frappe.connect()
    
    installed_apps = frappe.get_single("Installed Applications")
    
    for app in installed_apps.installed_applications:
        if app.app_name == "gcihs_app":
            app.app_version = "25.04.3"
        elif app.app_name == "library":
            app.app_version = "25.04.1"
    
    installed_apps.save()
    frappe.db.commit()
    print("Updated app versions successfully!")

if __name__ == "__main__":
    update_versions()
