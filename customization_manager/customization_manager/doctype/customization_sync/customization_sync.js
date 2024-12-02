// Copyright (c) 2024, improwised and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Customization Sync', {
// 	// refresh: function(frm) {

// 	// }
// });


frappe.ui.form.on('Customization Sync', {
    refresh: function(frm) {
        frm.add_custom_button(__('Sync Customizations'), function() {
            let filters = [];
            // Collect all selected DocTypes and filters from the table
            frm.doc.customization_sync_filter.forEach(function(row) {
                filters.push({
                    doctype: row.document_type,
                    fieldname: row.field_name,
					value: row.field_value,
                });
            });
			console.log("filttered items are ",filters)

            // Trigger the backend sync process
            frappe.call({
				method: "customization_manager.customization_manager.doctype.customization_sync.customization_sync.trigger_sync",
                args: {
                    source_site: frm.doc.source_site,
                    target_site: frm.doc.target_site,
                    filters: filters
                },
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(__('Sync initiated successfully!'));
                    }
                }
            });
        });
    }
});
