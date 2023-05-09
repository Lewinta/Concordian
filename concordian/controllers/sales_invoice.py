import frappe

def validate(doc, event):
    fetch_commission_percentage(doc)

def fetch_commission_percentage(doc):
    for item in doc.items:
        item.commission = frappe.db.get_value(
            "Item Group",
            item.item_group,
            "commission"
        )