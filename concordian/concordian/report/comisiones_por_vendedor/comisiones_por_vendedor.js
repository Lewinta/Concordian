// Copyright (c) 2023, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Comisiones por Vendedor"] = {
	"filters": [
		{
			"label": "Desde",
			"fieldname": "from_date",
			"fieldtype": "Date",
			"default": frappe.datetime.month_start()
		},
		{
			"label": "Hasta",
			"fieldname": "to_date",
			"fieldtype": "Date",
			"default": frappe.datetime.month_end()
		},
		{
			"label": __("Sales Partner"),
			"fieldname": "sales_partner",
			"fieldtype": "Link",
			"options": "Sales Partner",
		},
		{
			"label": __("View Details"),
			"fieldname": "view_details",
			"fieldtype": "Check",
		},

	]
};
