from odoo import _, fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    enable_po_validation_on_create = fields.Boolean("Enable Non-Moving & Stock Clearance Check")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_po_validation_on_create = fields.Boolean(
        'Enable Non-Moving & Stock Clearance Check',
        readonly=False,
        related="company_id.enable_po_validation_on_create"
    )
