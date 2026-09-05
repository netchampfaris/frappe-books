"""Seed a Books site with a realistic demo company, catalogue, and history.

Run it on a test site with::

	bench --site books.localhost execute frappe_books.demo.create_demo_data

Pass ``--kwargs "{'force': True}"`` to add another batch of transactions on a
site that already has some.
"""

from __future__ import annotations

import random
from datetime import datetime, time, timedelta
from pathlib import Path

import frappe
from frappe.utils import add_months, get_first_day, getdate, today

from frappe_books.setup_service import run_setup

SEED = 20260906
COMPANY = "Kaapi & Co."
OWNER_NAME = "Vandana Rao"
OWNER_EMAIL = "vandana@kaapiandco.example.com"
BANK = "HDFC Bank"
COMPANY_GSTIN = "29AABCK4521M1Z7"
MONTHS_OF_HISTORY = 6

ITEM_GROUPS = (
	("Coffee", "GST-5", "0901"),
	("Tea", "GST-5", "0902"),
	("Beverages", "GST-12", "2202"),
	("Snacks", "GST-18", "1905"),
	("Merchandise", "GST-18", "6912"),
	("Workshops", "GST-18", "9985"),
)

# name, group, sale rate, cost, tax, unit, image file, description
ITEMS = (
	(
		"Artisan Filter Coffee",
		"Coffee",
		450,
		260,
		"GST-5",
		"Unit",
		"artisan-filter-coffee.jpg",
		"Chikmagalur arabica, medium roast, 250 g pack for South Indian filter brewing.",
	),
	(
		"Cold Brew Concentrate",
		"Coffee",
		380,
		215,
		"GST-18",
		"Unit",
		"cold-brew-concentrate.jpg",
		"Sixteen-hour steeped concentrate, 500 ml bottle, makes eight servings.",
	),
	(
		"Single Origin Espresso Beans",
		"Coffee",
		760,
		430,
		"GST-5",
		"Unit",
		None,
		"Baba Budangiri estate beans roasted for espresso, 500 g whole bean.",
	),
	(
		"Roaster's Choice Sampler",
		"Coffee",
		999,
		620,
		"GST-5",
		"Unit",
		None,
		"Four 100 g pouches from the current season's lots.",
	),
	(
		"Masala Tea Collection",
		"Tea",
		520,
		290,
		"GST-5",
		"Unit",
		"masala-tea-collection.jpg",
		"Six spiced blends in a gift tin, 30 g each.",
	),
	(
		"Assam Breakfast Leaf Tea",
		"Tea",
		340,
		185,
		"GST-5",
		"Unit",
		None,
		"Second flush Assam orthodox leaf, 250 g.",
	),
	(
		"Nilgiri Green Tea",
		"Tea",
		420,
		240,
		"GST-5",
		"Unit",
		None,
		"High-grown Nilgiri green tea, 200 g.",
	),
	(
		"Mango Sparkler",
		"Beverages",
		120,
		62,
		"GST-12",
		"Unit",
		"mango-sparkler.jpg",
		"Sparkling Alphonso mango cooler, 300 ml.",
	),
	(
		"Butter Cookie Tin",
		"Snacks",
		260,
		140,
		"GST-18",
		"Unit",
		"butter-cookie-tin.jpg",
		"Danish-style butter cookies baked in Bengaluru, 400 g tin.",
	),
	(
		"Energy Bar Variety Pack",
		"Snacks",
		480,
		280,
		"GST-18",
		"Unit",
		"energy-bar-variety-pack.jpg",
		"Twelve date and nut bars in four flavours.",
	),
	(
		"Roasted Almond Brittle",
		"Snacks",
		210,
		112,
		"GST-18",
		"Unit",
		None,
		"Jaggery and almond brittle, 200 g.",
	),
	(
		"Ceramic Pour Over Dripper",
		"Merchandise",
		1450,
		820,
		"GST-18",
		"Unit",
		None,
		"Stoneware V-cone dripper with a matte glaze.",
	),
	(
		"Insulated Travel Tumbler",
		"Merchandise",
		890,
		495,
		"GST-18",
		"Unit",
		None,
		"Double-walled steel tumbler, 350 ml.",
	),
	(
		"Kaapi Canvas Tote",
		"Merchandise",
		550,
		290,
		"GST-12",
		"Unit",
		None,
		"Twelve-ounce cotton canvas tote, screen printed.",
	),
)

SERVICE_ITEMS = (
	("Barista Workshop", "Workshops", 2500, "GST-18", "Weekend brewing class for up to eight people."),
	("Espresso Machine Servicing", "Workshops", 1800, "GST-18", "On-site descale and group head service."),
)

PURCHASE_ONLY_ITEMS = (
	("Kraft Packaging Boxes", 26, "GST-12", "Printed kraft mailers, sold in packs of fifty."),
	("Compostable Cups", 4, "GST-18", "250 ml compostable cups with lids."),
)

# name, city, state, gst type, gstin, email, phone
CUSTOMERS = (
	(
		"Bluebird Cafe",
		"Bengaluru",
		"Karnataka",
		"Registered Regular",
		"29AACCB3921K1ZP",
		"orders@bluebirdcafe.example.com",
		"+91 80 4123 7781",
	),
	(
		"The Reading Room",
		"Bengaluru",
		"Karnataka",
		"Registered Regular",
		"29AAGCR7712L1ZQ",
		"hello@readingroom.example.com",
		"+91 80 4552 1190",
	),
	(
		"Sunrise Hotels",
		"Mysuru",
		"Karnataka",
		"Registered Regular",
		"29AABCS5533N1ZD",
		"purchase@sunrisehotels.example.com",
		"+91 821 244 5510",
	),
	(
		"Orchard Grocers",
		"Bengaluru",
		"Karnataka",
		"Registered Regular",
		"29AAECO1188P1ZK",
		"buying@orchardgrocers.example.com",
		"+91 80 4009 3312",
	),
	(
		"Highland Coffee House",
		"Chennai",
		"Tamil Nadu",
		"Registered Regular",
		"33AAFCH2204Q1ZB",
		"accounts@highlandcoffee.example.com",
		"+91 44 2811 6620",
	),
	(
		"Vista Corporate Services",
		"Hyderabad",
		"Telangana",
		"Registered Regular",
		"36AAGCV9910R1ZT",
		"admin@vistacorp.example.com",
		"+91 40 2355 8890",
	),
	(
		"Meera Krishnan",
		"Bengaluru",
		"Karnataka",
		"Consumer",
		None,
		"meera.k@example.com",
		"+91 98450 22118",
	),
	(
		"Arjun Sethi",
		"Pune",
		"Maharashtra",
		"Consumer",
		None,
		"arjun.sethi@example.com",
		"+91 98220 71145",
	),
	(
		"Farida Sheikh",
		"Bengaluru",
		"Karnataka",
		"Unregistered",
		None,
		"farida.s@example.com",
		"+91 99000 45521",
	),
	(
		"Walk-in Customer",
		"Bengaluru",
		"Karnataka",
		"Consumer",
		None,
		None,
		None,
	),
)

SUPPLIERS = (
	(
		"Coorg Estate Growers",
		"Madikeri",
		"Karnataka",
		"Registered Regular",
		"29AAACC1120J1ZR",
		"sales@coorgestates.example.com",
		"+91 8272 229 114",
	),
	(
		"Nilgiri Tea Traders",
		"Coonoor",
		"Tamil Nadu",
		"Registered Regular",
		"33AABCN4471H1ZV",
		"trade@nilgiritea.example.com",
		"+91 423 223 7788",
	),
	(
		"Fresh Bites Foods",
		"Bengaluru",
		"Karnataka",
		"Registered Regular",
		"29AAGCF3390D1ZW",
		"orders@freshbites.example.com",
		"+91 80 2266 4412",
	),
	(
		"Ceramica Home",
		"Jaipur",
		"Rajasthan",
		"Registered Regular",
		"08AADCC7781F1ZL",
		"wholesale@ceramicahome.example.com",
		"+91 141 405 2210",
	),
	(
		"Crest Packaging Solutions",
		"Bengaluru",
		"Karnataka",
		"Registered Regular",
		"29AAJCC2214B1ZS",
		"supply@crestpack.example.com",
		"+91 80 4771 3390",
	),
)

SUPPLIER_CATALOGUE = {
	"Coorg Estate Growers": (
		"Artisan Filter Coffee",
		"Single Origin Espresso Beans",
		"Cold Brew Concentrate",
		"Roaster's Choice Sampler",
	),
	"Nilgiri Tea Traders": ("Masala Tea Collection", "Assam Breakfast Leaf Tea", "Nilgiri Green Tea"),
	"Fresh Bites Foods": (
		"Butter Cookie Tin",
		"Energy Bar Variety Pack",
		"Roasted Almond Brittle",
		"Mango Sparkler",
	),
	"Ceramica Home": ("Ceramic Pour Over Dripper", "Insulated Travel Tumbler", "Kaapi Canvas Tote"),
	"Crest Packaging Solutions": ("Kraft Packaging Boxes", "Compostable Cups"),
}

WHOLESALE_CUSTOMERS = (
	"Bluebird Cafe",
	"The Reading Room",
	"Sunrise Hotels",
	"Orchard Grocers",
	"Highland Coffee House",
	"Vista Corporate Services",
)
RETAIL_CUSTOMERS = ("Meera Krishnan", "Arjun Sethi", "Farida Sheikh", "Walk-in Customer")

MONTHLY_EXPENSES = (
	("Office Rent", 28000, "Store and roastery rent"),
	("Salary", 58000, "Team payroll"),
	("Utility Expenses", 6400, "Power and water"),
	("Marketing Expenses", 9500, "Local campaigns and tastings"),
)

# A submitted Shipment relieves stock at the *selling* rate, so shipping every
# invoice would leave no gross margin at all. Ship most of them and leave the rest
# pending delivery, which is what a real order book looks like anyway.
SHIPPED_SHARE = 0.55
# Purchase invoice rows post here instead of to the item's expense account: the
# matching Purchase Receipt clears it into Stock In Hand, so goods are capitalised
# once instead of being expensed on the invoice and stocked on the receipt.
PURCHASE_ACCOUNT = "Stock Received But Not Billed"
OPENING_STOCK_QUANTITY = 150
# Invoices older than this are treated as settled; only recent ones stay outstanding.
SETTLED_AFTER_DAYS = 45

LEADS = (
	("Copper Kettle Bistro", "Interested", "chef@copperkettle.example.com", "+91 99860 33210"),
	("Sona Wellness Studio", "Open", "front.desk@sonawellness.example.com", "+91 98801 55432"),
	("Grainhouse Bakery", "Quotation", "owner@grainhouse.example.com", "+91 97400 11229"),
)


DEMO_DOCTYPES = (
	# Transactions first: ledgers, then the documents that wrote them.
	"Books Ledger Entry",
	"Books Stock Ledger Entry",
	"Books Loyalty Point Entry",
	"Books Payment For",
	"Books Payment",
	"Books Applied Coupon Codes",
	"Books Pricing Rule Detail",
	"Books Tax Summary",
	"Books Sales Invoice Item",
	"Books Sales Invoice",
	"Books Purchase Invoice Item",
	"Books Purchase Invoice",
	"Books Sales Quote Item",
	"Books Sales Quote",
	"Books Shipment Item",
	"Books Shipment",
	"Books Purchase Receipt Item",
	"Books Purchase Receipt",
	"Books Stock Movement Item",
	"Books Stock Movement",
	"Books Journal Entry Account",
	"Books Journal Entry",
	"Books Opening Cash",
	"Books Opening Amounts",
	"Books Closing Cash",
	"Books Closing Amounts",
	"Books Pos Closing Shift",
	"Books Pos Opening Shift",
	"Books Serial Number",
	"Books Batch",
	# Masters the seeder owns.
	"Books Coupon Code",
	"Books Pricing Rule Item",
	"Books Pricing Rule",
	"Books Price List Item",
	"Books Price List",
	"Books Collection Rules Items",
	"Books Loyalty Program",
	"Books Pos Profile",
	"Books Item",
	"Books Item Group",
	"Books Lead",
	"Books Party",
	"Books Address",
)


def clear_demo_data() -> None:
	"""Wipe every record the seeder creates. Test sites only — this deletes, it does not cancel."""
	for doctype in DEMO_DOCTYPES:
		frappe.db.delete(doctype)
	frappe.db.delete("Books Location", {"name": ("!=", "Stores")})
	frappe.db.delete("Books Payment Method", {"name": ("!=", "Cash")})
	frappe.db.sql("update `tabBooks Number Series` set current = start - 1")
	frappe.db.set_single_value("Books Pos Settings", "is_shift_open", 0)
	frappe.db.commit()


def create_demo_data(force: bool = False) -> dict:
	"""Set up the company if needed, then seed masters and a year-to-date history."""
	if frappe.db.count("Books Sales Invoice") and not force:
		frappe.throw("This site already has sales invoices. Re-run with force=True to add another batch.")

	rng = random.Random(SEED)
	ensure_setup()
	enable_features()
	created = {
		"item_groups": ensure_item_groups(),
		"items": ensure_items(),
		"parties": ensure_parties(),
		"locations": ensure_locations(),
		"payment_methods": ensure_payment_methods(),
		"price_list": ensure_price_list(),
		"pos_profile": ensure_pos_profile(),
		"loyalty_program": ensure_loyalty_program(),
		"pricing_rule": ensure_pricing_rule(),
		"leads": ensure_leads(),
	}

	start = getdate(frappe.db.get_single_value("Books Accounting Settings", "fiscal_year_start"))
	end = getdate(today())
	# Opening balances sit on the day before the year opens, so they do not show up
	# as trading activity in the first month's figures.
	opening_date = start - timedelta(days=1)
	created["opening_entry"] = create_opening_balances(opening_date)
	created["opening_stock"] = create_opening_stock(rng, opening_date)
	created["purchase_invoices"] = create_purchase_invoices(rng, start, end)
	created["sales_invoices"] = create_sales_invoices(rng, start, end)
	created["sales_quotes"] = create_sales_quotes(rng, end)
	created["journal_entries"] = create_expense_entries(start, end)
	created["stock_transfer"] = create_stock_transfer(end)
	created["stock_write_off"] = create_stock_write_off(end)
	created["pos_shift"] = open_pos_shift()

	frappe.db.commit()
	return created


# ---------------------------------------------------------------- setup


def ensure_setup() -> None:
	if frappe.db.get_single_value("Books Setup Wizard", "completed"):
		return

	start = fiscal_year_start()
	wizard = frappe.get_single("Books Setup Wizard")
	wizard.update(
		{
			"company_name": COMPANY,
			"fullname": OWNER_NAME,
			"email": OWNER_EMAIL,
			"country": "India",
			"currency": "INR",
			"bank_name": BANK,
			"chart_of_accounts": "Standard",
			"fiscal_year_start": start,
			"fiscal_year_end": add_months(start, 12) - timedelta(days=1),
		}
	)
	wizard.save(ignore_permissions=True)
	run_setup(wizard)


def fiscal_year_start():
	"""Indian fiscal year (April to March) containing today."""
	current = getdate(today())
	year = current.year if current.month >= 4 else current.year - 1
	return getdate(f"{year}-04-01")


def enable_features() -> None:
	settings = frappe.get_single("Books Accounting Settings")
	settings.update(
		{
			"gstin": COMPANY_GSTIN,
			"enable_discounting": 1,
			"enable_inventory": 1,
			"enable_price_list": 1,
			"enable_invoice_returns": 1,
			"enable_lead": 1,
			"enable_pricing_rule": 1,
			"enable_coupon_code": 1,
			"enable_loyalty_program": 1,
			"enable_partial_payment": 1,
			"enableitem_group": 1,
		}
	)
	settings.save(ignore_permissions=True)

	inventory = frappe.get_single("Books Inventory Settings")
	inventory.update({"enable_point_of_sale": 1, "enable_uom_conversions": 1})
	inventory.save(ignore_permissions=True)


# ---------------------------------------------------------------- masters


def ensure_item_groups() -> list[str]:
	names = []
	for name, tax, hsn in ITEM_GROUPS:
		names.append(insert_if_missing("Books Item Group", name, {"tax": tax, "hsn_code": hsn}))
	return names


def ensure_items() -> list[str]:
	names = []
	for name, group, rate, _cost, tax, unit, image, description in ITEMS:
		names.append(
			insert_if_missing(
				"Books Item",
				name,
				{
					"item_code": item_code(name),
					"item_group": group,
					"item_usage": "Both",
					"item_type": "Product",
					"unit": unit,
					"rate": rate,
					"description": description,
					"tax": tax,
					"income_account": "Sales",
					"expense_account": "Cost of Goods Sold",
					"track_item": 1,
				},
			)
		)
		if image:
			attach_image(name, image)

	for name, group, rate, tax, description in SERVICE_ITEMS:
		names.append(
			insert_if_missing(
				"Books Item",
				name,
				{
					"item_code": item_code(name),
					"item_group": group,
					"item_usage": "Sales",
					"item_type": "Service",
					"unit": "Hour",
					"rate": rate,
					"description": description,
					"tax": tax,
					"income_account": "Service",
					"expense_account": "Cost of Goods Sold",
				},
			)
		)

	for name, rate, tax, description in PURCHASE_ONLY_ITEMS:
		names.append(
			insert_if_missing(
				"Books Item",
				name,
				{
					"item_code": item_code(name),
					"item_group": "Merchandise",
					"item_usage": "Purchases",
					"item_type": "Product",
					"unit": "Unit",
					"rate": rate,
					"description": description,
					"tax": tax,
					"income_account": "Sales",
					"expense_account": "Cost of Goods Sold",
					"track_item": 1,
				},
			)
		)
	return names


def item_code(name: str) -> str:
	words = [word for word in name.replace("'", "").split() if word]
	return "-".join(word[:3].upper() for word in words[:3])


def attach_image(item: str, filename: str) -> None:
	if frappe.db.get_value("Books Item", item, "image"):
		return
	path = Path(frappe.get_app_path("frappe_books")).parent / "demo_assets" / "pos-item-images" / filename
	if not path.exists():
		return
	file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"content": path.read_bytes(),
			"is_private": 0,
			"attached_to_doctype": "Books Item",
			"attached_to_name": item,
			"attached_to_field": "image",
		}
	).insert(ignore_permissions=True)
	frappe.db.set_value("Books Item", item, "image", file.file_url, update_modified=False)


def ensure_parties() -> list[str]:
	names = []
	for group, role, account in ((CUSTOMERS, "Customer", "Debtors"), (SUPPLIERS, "Supplier", "Creditors")):
		for name, city, state, gst_type, gstin, email, phone in group:
			address = insert_if_missing(
				"Books Address",
				f"{name} - {city}",
				{
					"address_line1": f"{rng_street(name)}",
					"city": city,
					"state": state,
					"country": "India",
					"postal_code": postal_code(city),
					"email_address": email,
					"phone": phone,
				},
			)
			names.append(
				insert_if_missing(
					"Books Party",
					name,
					{
						"role": role,
						"email": email,
						"phone": phone,
						"address": address,
						"default_account": account,
						"currency": "INR",
						"gst_type": gst_type,
						"gstin": gstin,
					},
				)
			)
	return names


def rng_street(name: str) -> str:
	streets = (
		"12 Church Street",
		"48 Residency Road",
		"7 Lavelle Road",
		"210 Commercial Street",
		"3 Brigade Road",
		"91 Infantry Road",
		"56 Cunningham Road",
		"18 Museum Road",
	)
	return streets[sum(map(ord, name)) % len(streets)]


def postal_code(city: str) -> str:
	codes = {
		"Bengaluru": "560001",
		"Mysuru": "570001",
		"Chennai": "600002",
		"Hyderabad": "500081",
		"Pune": "411001",
		"Madikeri": "571201",
		"Coonoor": "643101",
		"Jaipur": "302001",
	}
	return codes.get(city, "560001")


def ensure_locations() -> list[str]:
	return [
		insert_if_missing("Books Location", "Stores", {}),
		insert_if_missing("Books Location", "Roastery Warehouse", {}),
	]


def ensure_payment_methods() -> list[str]:
	return [
		insert_if_missing("Books Payment Method", "Cash", {"type": "Cash", "account": "Cash"}),
		insert_if_missing("Books Payment Method", "Bank Transfer", {"type": "Transfer", "account": BANK}),
		insert_if_missing("Books Payment Method", "Card", {"type": "Bank", "account": BANK}),
		insert_if_missing("Books Payment Method", "UPI", {"type": "Transfer", "account": BANK}),
	]


def ensure_price_list() -> str:
	rows = [
		{"item": name, "unit": unit, "rate": round(rate * 0.85)}
		for name, _group, rate, _cost, _tax, unit, _image, _description in ITEMS
	]
	return insert_if_missing(
		"Books Price List",
		"Wholesale",
		{"is_enabled": 1, "is_sales": 1, "price_list_item": rows},
	)


def ensure_pos_profile() -> str:
	return insert_if_missing(
		"Books Pos Profile",
		"Storefront Counter",
		{
			"pos_customer": "Walk-in Customer",
			"inventory": "Stores",
			"pos_ui": "Modern",
			"item_visibility": "Inventory Items",
			"can_edit_discount": 1,
			"hide_unavailable_items": 1,
			"pos_print_template": "Business-POS - Sales Invoice",
		},
	)


def ensure_loyalty_program() -> str:
	start = fiscal_year_start()
	return insert_if_missing(
		"Books Loyalty Program",
		"Kaapi Club",
		{
			"is_enabled": 1,
			"from_date": start,
			"to_date": add_months(start, 24),
			"conversion_factor": 1,
			"expiry_duration": 365,
			"maximum_use": 0,
			"used": 0,
			"expense_account": "Marketing Expenses",
			"collection_rules": [
				{"tier_name": "Bronze", "collection_factor": 0.02, "minimum_total_spent": 0},
				{"tier_name": "Silver", "collection_factor": 0.04, "minimum_total_spent": 25000},
				{"tier_name": "Gold", "collection_factor": 0.06, "minimum_total_spent": 75000},
			],
		},
	)


def ensure_pricing_rule() -> str | None:
	if frappe.db.exists("Books Pricing Rule", {"title": "Festive Coffee Offer"}):
		return None
	rule = frappe.get_doc(
		{
			"doctype": "Books Pricing Rule",
			"number_series": "PRLE-",
			"title": "Festive Coffee Offer",
			"is_enabled": 1,
			"discount_type": "Price Discount",
			"price_discount_type": "percentage",
			"discount_percentage": 10,
			"priority": "1",
			"rounding_method": "round",
			"is_coupon_code_based": 1,
			"min_quantity": 2,
			"valid_from": fiscal_year_start(),
			"valid_to": add_months(fiscal_year_start(), 12),
			"applied_items": [
				{"item": "Artisan Filter Coffee"},
				{"item": "Cold Brew Concentrate"},
				{"item": "Roaster's Choice Sampler"},
			],
		}
	).insert(ignore_permissions=True)
	# The coupon docname is derived from coupon_name, so check that field instead.
	if not frappe.db.exists("Books Coupon Code", {"coupon_name": "Festive10"}):
		frappe.get_doc(
			{
				"doctype": "Books Coupon Code",
				"coupon_name": "Festive10",
				"is_enabled": 1,
				"pricing_rule": rule.name,
				"min_amount": 1000,
				"max_amount": 50000,
				"valid_from": fiscal_year_start(),
				"valid_to": add_months(fiscal_year_start(), 12),
				"maximum_use": 200,
				"used": 0,
			}
		).insert(ignore_permissions=True)
	return rule.name


def ensure_leads() -> list[str]:
	names = []
	for name, status, email, mobile in LEADS:
		names.append(
			insert_if_missing("Books Lead", name, {"status": status, "email": email, "mobile": mobile})
		)
	return names


# ---------------------------------------------------------------- transactions


def create_opening_balances(start) -> str:
	entry = frappe.get_doc(
		{
			"doctype": "Books Journal Entry",
			"number_series": "JV-",
			"entry_type": "Journal Entry",
			"posting_date": start,
			"user_remark": "Opening balances",
			"accounts": [
				{"account": BANK, "debit": 1650000, "credit": 0},
				{"account": "Cash", "debit": 60000, "credit": 0},
				{"account": "Opening Balance Equity", "debit": 0, "credit": 1710000},
			],
		}
	).insert(ignore_permissions=True)
	entry.submit()
	return entry.name


def create_opening_stock(rng, start) -> list[str]:
	"""Buy in the shelf stock the company starts the year with."""
	names = []
	for supplier, catalogue in SUPPLIER_CATALOGUE.items():
		items = [
			{
				"item": name,
				"quantity": OPENING_STOCK_QUANTITY,
				"rate": cost_of(name),
				"account": PURCHASE_ACCOUNT,
			}
			for name in catalogue
		]
		invoice = frappe.get_doc(
			{
				"doctype": "Books Purchase Invoice",
				"number_series": "PINV-",
				"party": supplier,
				"date": at(start, 10),
				"items": items,
				"make_auto_stock_transfer": 1,
				"terms": "Opening stock purchase.",
			}
		).insert(ignore_permissions=True)
		invoice.submit()
		pay_invoice(invoice, "Pay", "Creditors", BANK, "Bank Transfer", start, rng)
		names.append(invoice.name)
	return names


def create_purchase_invoices(rng, start, end) -> list[str]:
	names = []
	month = get_first_day(start)
	while month <= end:
		for supplier, catalogue in SUPPLIER_CATALOGUE.items():
			day = min(rng.randint(3, 24), days_in_month(month))
			date = getdate(month.replace(day=day))
			if date > end:
				continue
			items = [
				{
					"item": name,
					"quantity": rng.choice((24, 36, 48, 60)),
					"rate": cost_of(name),
					"account": PURCHASE_ACCOUNT,
				}
				for name in rng.sample(catalogue, k=min(len(catalogue), rng.randint(2, 3)))
			]
			invoice = frappe.get_doc(
				{
					"doctype": "Books Purchase Invoice",
					"number_series": "PINV-",
					"party": supplier,
					"date": at(date, 11),
					"items": items,
					"make_auto_stock_transfer": 1,
					"terms": "Payment due within 30 days of receipt.",
				}
			).insert(ignore_permissions=True)
			invoice.submit()
			names.append(invoice.name)
			if is_settled(date, end) or rng.random() < 0.5:
				paid_on = min(date + timedelta(days=rng.randint(5, 25)), end)
				pay_invoice(invoice, "Pay", "Creditors", BANK, "Bank Transfer", paid_on, rng)
		month = get_first_day(add_months(month, 1))
	return names


def create_sales_invoices(rng, start, end) -> list[str]:
	names = []
	date = start
	sellable = [row[0] for row in ITEMS]
	services = [row[0] for row in SERVICE_ITEMS]
	while date <= end:
		if date.weekday() == 6:
			date += timedelta(days=1)
			continue
		for _ in range(rng.choice((0, 1, 1, 2, 2, 3))):
			retail = rng.random() < 0.55
			party = rng.choice(RETAIL_CUSTOMERS if retail else WHOLESALE_CUSTOMERS)
			pool = sellable if retail else sellable + services
			lines = rng.randint(1, 2) if retail else rng.randint(2, 4)
			items = [
				{
					"item": name,
					"quantity": service_or_retail_quantity(rng, name in services, retail),
				}
				for name in rng.sample(pool, k=min(lines, len(pool)))
			]
			values = {
				"doctype": "Books Sales Invoice",
				"number_series": "SINV-",
				"party": party,
				"date": at(date, rng.randint(10, 19)),
				"items": items,
				"make_auto_stock_transfer": int(rng.random() < SHIPPED_SHARE),
			}
			if retail:
				values["is_pos"] = 1
			else:
				values["terms"] = "Net 15. Please quote the invoice number with the transfer."
				if rng.random() < 0.3:
					values["set_discount_amount"] = 0
					values["discount_percent"] = rng.choice((5, 7.5, 10))
			invoice = frappe.get_doc(values).insert(ignore_permissions=True)
			invoice.submit()
			names.append(invoice.name)

			if retail:
				method = rng.choice(("Cash", "UPI", "Card"))
				account = "Cash" if method == "Cash" else BANK
				pay_invoice(invoice, "Receive", "Debtors", account, method, date, rng)
			elif is_settled(date, end) or rng.random() < 0.45:
				paid_on = min(date + timedelta(days=rng.randint(2, 20)), end)
				method = rng.choice(("Bank Transfer", "UPI", "Card"))
				partial = not is_settled(date, end) and rng.random() < 0.3
				pay_invoice(invoice, "Receive", "Debtors", BANK, method, paid_on, rng, partial=partial)
		date += timedelta(days=1)
	return names


def pay_invoice(invoice, payment_type, account, payment_account, method, date, rng, partial=False):
	outstanding = frappe.db.get_value(invoice.doctype, invoice.name, "outstanding_amount")
	amount = round(float(outstanding) * (0.5 if partial else 1), 2)
	if amount <= 0:
		return None
	reference = "SalesInvoice" if invoice.doctype == "Books Sales Invoice" else "PurchaseInvoice"
	payment = frappe.get_doc(
		{
			"doctype": "Books Payment",
			"number_series": "PAY-",
			"party": invoice.party,
			"date": at(getdate(date), rng.randint(10, 18)),
			"payment_type": payment_type,
			"account": account,
			"payment_account": payment_account,
			"payment_method": method,
			"amount": amount,
			"reference_type": reference,
			"payment_references": [
				{
					"reference_type": invoice.doctype,
					"reference_name": invoice.name,
					"amount": amount,
				}
			],
		}
	).insert(ignore_permissions=True)
	payment.submit()
	return payment.name


def create_sales_quotes(rng, end) -> list[str]:
	names = []
	for offset, party in enumerate(("Sunrise Hotels", "Highland Coffee House", "Vista Corporate Services")):
		date = end - timedelta(days=offset * 6 + 2)
		items = [
			{"item": name, "quantity": rng.randint(10, 30)}
			for name in rng.sample([row[0] for row in ITEMS], k=3)
		]
		quote = frappe.get_doc(
			{
				"doctype": "Books Sales Quote",
				"number_series": "SQUOT-",
				"reference_type": "Books Party",
				"party": party,
				"date": at(date, 12),
				"items": items,
				"terms": "Valid for 30 days. Prices include GST.",
			}
		).insert(ignore_permissions=True)
		quote.submit()
		names.append(quote.name)
	return names


def create_expense_entries(start, end) -> list[str]:
	names = []
	month = get_first_day(start)
	while month <= end:
		for account, amount, remark in MONTHLY_EXPENSES:
			date = getdate(month.replace(day=min(28, days_in_month(month))))
			if date > end:
				continue
			entry = frappe.get_doc(
				{
					"doctype": "Books Journal Entry",
					"number_series": "JV-",
					"entry_type": "Bank Entry",
					"posting_date": date,
					"user_remark": f"{remark} - {date.strftime('%B %Y')}",
					"accounts": [
						{"account": account, "debit": amount, "credit": 0},
						{"account": BANK, "debit": 0, "credit": amount},
					],
				}
			).insert(ignore_permissions=True)
			entry.submit()
			names.append(entry.name)
		month = get_first_day(add_months(month, 1))
	return names


def create_stock_transfer(end) -> str:
	rows = [
		{
			"item": name,
			"from_location": "Stores",
			"to_location": "Roastery Warehouse",
			"quantity": 25,
			"transfer_quantity": 25,
			"unit_conversion_factor": 1,
			"rate": cost_of(name),
		}
		for name in ("Artisan Filter Coffee", "Masala Tea Collection", "Butter Cookie Tin")
	]
	movement = frappe.get_doc(
		{
			"doctype": "Books Stock Movement",
			"number_series": "SMOV-",
			"movement_type": "MaterialTransfer",
			"date": at(end - timedelta(days=3), 15),
			"items": rows,
		}
	).insert(ignore_permissions=True)
	movement.submit()
	return movement.name


def create_stock_write_off(end) -> str:
	"""Write off the odd damaged or expired pack, the way a shop actually does."""
	rows = [
		{
			"item": name,
			"from_location": "Stores",
			"quantity": quantity,
			"transfer_quantity": quantity,
			"unit_conversion_factor": 1,
			"rate": cost_of(name),
		}
		for name, quantity in (("Mango Sparkler", 12), ("Butter Cookie Tin", 4), ("Cold Brew Concentrate", 3))
	]
	movement = frappe.get_doc(
		{
			"doctype": "Books Stock Movement",
			"number_series": "SMOV-",
			"movement_type": "MaterialIssue",
			"date": at(end - timedelta(days=9), 17),
			"items": rows,
		}
	).insert(ignore_permissions=True)
	movement.submit()
	return movement.name


def open_pos_shift() -> str | None:
	"""Leave the counter open so the POS screen is usable straight away."""
	if frappe.db.get_single_value("Books Pos Settings", "is_shift_open"):
		return None
	denominations = ((500, 6), (200, 5), (100, 10), (50, 8), (20, 10))
	opening_cash = [{"denomination": value, "count": count} for value, count in denominations]
	total = sum(value * count for value, count in denominations)
	shift = frappe.get_doc(
		{
			"doctype": "Books Pos Opening Shift",
			"opening_date": at(getdate(today()), 9),
			"opening_cash": opening_cash,
			"opening_amounts": [
				{"payment_method": "Cash", "amount": total},
				{"payment_method": "Card", "amount": 0},
				{"payment_method": "UPI", "amount": 0},
				{"payment_method": "Bank Transfer", "amount": 0},
			],
		}
	).insert(ignore_permissions=True)
	return shift.name


# ---------------------------------------------------------------- helpers


def service_or_retail_quantity(rng, is_service: bool, retail: bool) -> int:
	"""Services are booked by the session, goods by the case."""
	if is_service:
		return rng.randint(1, 2)
	return rng.randint(1, 3) if retail else rng.randint(4, 14)


def is_settled(date, end) -> bool:
	return (end - date).days > SETTLED_AFTER_DAYS


def cost_of(item: str) -> float:
	for name, _group, _rate, cost, _tax, _unit, _image, _description in ITEMS:
		if name == item:
			return cost
	for name, rate, _tax, _description in PURCHASE_ONLY_ITEMS:
		if name == item:
			return rate
	return 0


def at(date, hour: int) -> datetime:
	return datetime.combine(getdate(date), time(hour, 0))


def days_in_month(date) -> int:
	next_month = get_first_day(add_months(date, 1))
	return (next_month - timedelta(days=1)).day


def insert_if_missing(doctype: str, name: str, values: dict) -> str:
	if frappe.db.exists(doctype, name):
		return name
	frappe.get_doc({"doctype": doctype, "name": name, **values}).insert(ignore_permissions=True)
	return name
