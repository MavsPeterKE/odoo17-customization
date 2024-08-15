from odoo import fields, models, api
from datetime import datetime, timedelta


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_non_moving_product = fields.Boolean('is Non Moving Product', default=False)
    non_moving_period_days = fields.Integer(
        string="Non-Moving Period (days)",
        default=90,
        help="Number of days to consider a product as non-moving."
    )
    track_days = fields.Integer(
        string="Track Days ",
        default=90,
        help="Number of days to clear 50% of stock."
    )

    track_stock_clearance = fields.Boolean(
        string="Track Stock Clearance",
        help="Check on Product if 50% of stock has been cleared on PO creation"
    )
    enable_validation_on_po_create = fields.Boolean(compute='_compute_on_po_create')

    def _compute_on_po_create(self):
        company = self.env.company
        self.enable_validation_on_po_create = company.enable_po_validation_on_create
