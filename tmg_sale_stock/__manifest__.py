# -*- coding: utf-8 -*-
{
    'name': 'TMG: Sale & Stock',
    'summary': 'This feature should allow a user to define, on a single sale order line, multiple shipping addresses. Confirming such an order should generate one delivery order per delviery address and a single manufacturing order per line item.',
    'description':
    """
    This feature is designed to accomodate the following use cases:
    - The Magnet Group frequently ships products from a single order to multiple shipping addresses. (The average number of shipping addresses on a single order is 6.) Orders typically consist of a single type of item with a single specification and artwork.
    - Manufacturing orders will be used to describe the work necessary to produce a custom-printed item. Because of long setup times it is highly desireable to have a single manufacturing order represent a single print run.
    - Quantity pricing in Odoo is calculated using the quantity on a single sale order line item.
    - It is highly desireable to invoice a single type of item sold to a single customer on the same invoice line.
    1. Interface modificaions to the sale order:
    1.1. On the sale order line pop-out form view, the user should be able manage an in-form list of delivery addresses and the quantity of the item to be shipped to that address.
    1.2. This list should be populated by default with the SO delivery address and the entire SO line quantity
    1.3. When saving a sale order line:
    1.3.1. If the entire ordered quantity of the sale order line is not allocated, allocate the remainder to the default shipping address. Return a non-blocking warning message with the following text:
    "You have allocated less quantity to delivery addresses than were orders. The remaining units have been allocated to the order's shipping address."
    1.3.2. If the allocated quantity exceeds the ordered quantity, increase the ordered quantity to match the allocated quantity. Return a non-blocking warning message with the following text:
    "You have allocated more quantity to delivery addresses than were ordered. The ordered quantity has been increased. To decrease the ordered quantity, unallocate items from their delivery addresses."
    Technical Note:
    Create a new model sale.order.line.address with the following fields
    -sale_line_id (corresponds to delivery_partner_ids on the sale.order.line)
    -product_id
    -quantity
    -partner_id
    -tax_ids?
    Add a new o2m field the the sale order line, delivery_partner_ids.
    To the bottom of the sale order line pop-out form view, add a bottom-editable tree view for delivery_partner_ids with the following fields:
    -partner_id
    -quantity
    On creation of a sale order line, create one line.address record where:
    sale_line_id = self
    partner_id = self.shipping_partner_id
    product_id = self.product_id
    quantity = self.quantity
    1.4. A user should be able to import a csv or excel file to create line.address records. This import file is expected to have some or all of the following fields and should allow the user to reference existing addresses or create them at the time of import.
    name
    internal reference (res.partner)
    parent contact
    street1
    street2
    state
    zip
    country
    phone
    email
    quantity
    2. When a sale order is confirmed, create one delivery order per delivery address. 
    Limitation Note:
    Scheduled delivery date will be set at the sale order line level, so any modifications to schedule date on a per-line address level must be made after confirmation of the sale order.
    Technical Note:
    On confirmation of the sale order, create one procurement for each line line.address.
    3. Create a draft state for manufacturing orders. A manufacturing order should be in state draft until it is manually confirmed by a user. MOs in a draft state should not affect the stock forecast. If a new procurement is created where product and all attribute values match an existing draft MO, add the items to the MO rather than creating a new one.
    3.1. The user should be able confirm multiple manufacturing orders at once by selecting them in the list view and running an action.
    Technical Note: Create a contextual action for the mrp.production named "Confirm Manufacturing Orders". 
    Acceptance Tests:
    Common preconfiguration for cases 1-4:
    Product P with routes MTO and Manufacture, and BoM with 1 component, product C.
    Product Q with routes MTO and Manufacture, and BoM with 1 component, product C.
    Partner D and partner E.
    Case 1: Single line item w/ splits
    Steps
    1. Create a sale order. Set the delivery address to partner D.
    2. Add a line to the order for product P, quantity 2.
    3. Click on the line item to raise the sale order line form view
    4. In the delviery addresess field on the order line form view:
    4.1. Set the existing split with partner D quantity == 1
    4.2. Create a new split with partner E and quantity == 1
    5. Confirm the sale order
    Expected behavior:
    1. Two delivery orders, each for quantity 1 of product P. One transfer should have partner D and the other partner E.
    2. One manufacturing order for quantity 2 of product p in state == draft
    Case 2: Two line items w/ overlapping splits
    Steps
    1. Create a sale order. Set the delivery address to partner D.
    2. Add a line to the order for product P, quantity 2.
    3. Click on the line item to raise the sale order line form view
    4. In the delivery addresses field on the order line form view:
    4.1. Set the existing address with partner D quantity == 1
    4.2. Add a new address with partner E and quantity == 1
    5. Repeat steps 2-4 with product Q
    6. Confirm the sale order
    Expected behavior:
    1. Two delivery orders, each for quantity 1 each of product P and Q. One transfer should have partner D and the other partner E.
    2. Two manufacturing orders for quantity 2 each of products P and Q.
    Case 3: Single line item w/o splits
    Steps:
    1. Create a sale order. Set the delivery address to partner D.
    2. Add a line to the order for product P, quantity 2.
    3. Confirm the sale order
    Expected behavior:
    1. One delivery order for quantity 2 product P, partner D
    2. One anufacturing order for quantity 2 product P
    Case 4: MTO product w/ manufacture in 3 steps
    Steps:
    0. Enable the manufacturing in 3 steps option for the warehouse.
    1. Create a sale order. Set the delivery address to partner D.
    2. Add a line to the order for product P, quantity 2.
    3. Click on the line item to raise the sale order line form view
    4. In the delviery addresess field on the order line form view:
    4.1. Set the existing split with partner D quantity == 1
    4.2. Create a new split with partner E and quantity == 1
    5. Confirm the sale order
    Expected behavior:
    1. Two delivery orders, each for quantity 1 of product P. One transfer should have partner D and the other partner E.
    2. One manufacturing order for quantity 2 of product p in state == draft
    3. One picking before manufacturing for quantity 2 of product C
    4. One putaway after manufacturing for quantity 2 of product P
    Case 5: Sale order line routes
    Additional configuration
    1. Enable routes on sale order lines and multi-step routes
    2. Enable multi-warehouse
    3. Create a second warehouse, "WH2"
    4. Modify the "Ship Only" route of the second warehouse as follows:
    4.1. Remove the served warehouse of the procurement group
    4.2. Enable selecting the route on the sale order line
    Steps
    1. Create a sale order. Set the delivery address to partner D.
    2. Add a line to the order for product P, quantity 2.
    3. Click on the line item to raise the sale order line form view
    4. In the delviery addresess field on the order line form view:
    4.1. Set the existing split with partner D quantity == 1
    4.2. Create a new split with partner E and quantity == 1
    5. Set the route WH2: Ship Only on the line 
    6. Repeat steps 1-4.
    7. Confirm the sale order.
    Expected behavior:
    In the first warehouse:
    1. Two delivery orders, each for quantity 1 of product P. One transfer should have partner D and the other partner E.
    2. One manufacturing order for quantity 2 of product p in state == draft
    In WH2:
    1. Two delivery orders, each for quantity 1 of product P. One transfer should have partner D and the other partner E.
    2. One manufacturing order for quantity 2 of product p in state == draft
    """,
    'license': 'OEEL-1',
    'author': 'Odoo Inc',
    'version': '0.1',
    'depends': ['sale_management', 'sale_stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
}