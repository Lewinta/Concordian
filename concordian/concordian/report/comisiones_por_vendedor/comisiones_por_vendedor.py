# Copyright (c) 2023, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr
from frappe.query_builder import Criterion, functions as fn

def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):	
	if filters.get("view_details"):
		columns = (
			(_("Sales Invoice"), "Link/Sales Invoice", 170),
			(_("Date"), "Date", 100),
			(_("Customer"),  "Data", 220),
			(_("Sales Partner"),  "Data", 160),
			(_("Item"),  "Data", 220),
			(_("Purchase Price"),  "Currency", 160),
			(_("Sale Price"),  "Currency", 160),
			(_("Qty"),  "int", 90),
			(_("Margin"), "Currency", 100),
			(_("Commission"), "Percent", 100),
			(_("Amount"), "Currency", 100),
		)
	else:
		columns = (
			(_("Sales Partner"),  "Data", 220),
			(_("Margin"),  "Currency", 120),
			(_("Commission"), "Currency", 120),
		)
	formatted_columns = []

	for label, fieldtype, width in columns:
		formatted_columns.append(
			get_formatted_column(_(label), fieldtype, width)
		)

	return formatted_columns

def get_fields(filters):
	"""
		Return sql fields ready to be used on a query
	"""
	if filters.get("view_details"):
		fields = (
			("Sales Invoice", "name"),
			("Sales Invoice", "posting_date"),
			("Sales Invoice", "customer"),
			("Sales Partner", "name"),
			("CONCAT('<b>',`tabSales Invoice Item`.item_code, '</b>:',`tabSales Invoice Item`.item_name )"),
			("Sales Invoice Item", "amount"),
			("Commissions by Item Group", "percentage"),
			("`tabSales Invoice Item`.amount * `tabCommissions by Item Group`.percentage / 100.0"),
		)
	else:
		fields = (
			("Sales Partner", "name"),
			("SUM(`tabSales Invoice Item`.amount) as amount"),
			("SUM(`tabSales Invoice Item`.amount * `tabCommissions by Item Group`.percentage / 100.0) as commission"),
		)
	sql_fields = []

	for args in fields:
		sql_field = get_field(args)
		sql_fields.append(sql_field)

	return ", ".join(sql_fields)
	
def get_data(filters):
	SINV = frappe.qb.DocType("Sales Invoice")
	SITM = frappe.qb.DocType("Sales Invoice Item")
	PINV = frappe.qb.DocType("Purchase Invoice")
	PITM = frappe.qb.DocType("Purchase Invoice Item")

	conditions = [
		SINV.docstatus == 1,
		PINV.docstatus == 1,
	]

	if filters.get('from_date'):
		conditions.append(SINV.posting_date >= filters.get('from_date'))
	
	if filters.get('to_date'):
		conditions.append(SINV.posting_date <= filters.get('to_date'))

	if filters.get('sales_partner'):
		conditions.append(SINV.sales_partner == filters.get('sales_partner'))
	if filters.get("view_details"):
		return	frappe.qb.from_(SINV).join(SITM).on(
			SINV.name == SITM.parent
		).join(PITM).on(
			SITM.item_code == PITM.item_code
		).join(PINV).on(
			PITM.parent == PINV.name
		).select(
			SINV.name,
			SINV.posting_date,
			SINV.customer,
			SINV.sales_partner,
			SITM.item_name.as_('item'),
			PITM.rate.as_('purchase_price'),
			SITM.rate.as_('sale_price'),
			SITM.qty,
			((SITM.rate - PITM.rate) * SITM.qty).as_('margin'),
			SITM.commission,
			((SITM.rate - PITM.rate) * SITM.qty * SITM.commission / 100.0).as_('amount')
		).where(
			Criterion.all(conditions)
		).run()
	else:
		return	frappe.qb.from_(SINV).join(SITM).on(
			SINV.name == SITM.parent
		).join(PITM).on(
			SITM.item_code == PITM.item_code
		).join(PINV).on(
			PITM.parent == PINV.name
		).select(
			SINV.sales_partner,
			fn.Sum(((SITM.rate - PITM.rate) * SITM.qty)).as_('margin'),
			fn.Sum(((SITM.rate - PITM.rate) * SITM.qty * SITM.commission / 100.0)).as_('amount')
		).where(
			Criterion.all(conditions)
		).groupby(SINV.sales_partner).run()


def get_field(args):
	if len(args) == 2:
		doctype, fieldname = args
	else:
		return args if isinstance(args, str) \
			else " ".join(args)

	sql_field = "`tab{doctype}`.`{fieldname}`" \
		.format(doctype=doctype, fieldname=fieldname)

	return sql_field

def get_formatted_column(label, fieldtype, width):
	# [label]:[fieldtype/Options]:width
	parts = (
		_(label),
		fieldtype,
		cstr(width)
	)
	return ":".join(parts)
