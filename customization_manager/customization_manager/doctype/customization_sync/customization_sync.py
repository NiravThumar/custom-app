import json
import frappe
from frappe.model.document import Document

class CustomizationSync(Document):
    pass


import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def trigger_sync(source_site, target_site, filters=None):
    print("----------inside Trigger sync----------------------")

    # Enqueue the sync job for background execution
    sync_customizations(source_site=source_site, target_site=target_site, filters=filters)
    return "Sync job has been enqueued!"

def sync_customizations(source_site, target_site, filters=None):
    print("----------inside sync_customization----------------------")

    # Initialize and connect to the source site
    frappe.init(site=source_site)
    frappe.connect()
    print("---------- frappe connected----------------------")
    all_records = {}  # To store records fetched from source

     # Deserialize filters from JSON string to Python list
    if filters:
        filters = json.loads(filters)  # Convert JSON string back to Python list
    for filter in filters:
        doc_type = filter.get('doctype')  # Get the DocType
        filtered_records = get_filtered_records(doc_type, filter)
        all_records[doc_type] = filtered_records


        # Sync the records for the current DocType
        # sync_records(doc_type, filtered_records)

    # Commit changes to source site
    frappe.db.commit()
    frappe.destroy()

    # Connect to the target site
    frappe.init(site=target_site)
    frappe.connect()

    print("connected to taret db -------------")
    # Loop over the filters again to sync the same records to the target site

    for doc_type, records in all_records.items():
        sync_records(doc_type, records)

    print("sync successfully -------------")
    

    frappe.db.commit()
    frappe.destroy()  # Disconnect from target site

    # Commit changes to the target site
    frappe.db.commit()
    frappe.destroy()

def get_filtered_records(doctype, filters):
    conditions = []

    # Apply filters based on user input
    if filters:
        if filters.get('field_name'):
            conditions.append(['field_name', '=', filters['field_name']])
        if filters.get('modified_after'):
            conditions.append(['modified', '>=', filters['modified_after']])
        if filters.get('custom_only') and doctype == 'DocType':
            conditions.append(['custom', '=', 1])

    # Dynamically fetch records from the specified doctype
    return frappe.get_all(doctype, filters=conditions, fields=['*'])

def sync_records(doctype, records):
    for record in records:
        record.pop('name', None)  # Remove 'name' to avoid conflicts
        record['doctype'] = doctype  # Set the correct DocType

        # Only insert if the record does not already exist on the target site
        if not frappe.db.exists(doctype, {'fieldname': record.get('fieldname')}):
            frappe.get_doc(record).insert(ignore_permissions=True)