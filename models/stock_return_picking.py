from odoo import fields, models, api,_
from datetime import datetime, timedelta


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def create_returns(self):
        for wizard in self:
            new_picking_id, pick_type_id = wizard._create_returns()
        # Override the context to disable all the potential filters that could have been set previously
        ctx = dict(self.env.context)
        ctx.update({
            'default_partner_id': self.picking_id.partner_id.id,
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_planning_issues': False,
            'search_default_available': False,
        })
        self._send_email()
        return {
            'name': _('Returned Picking'),
            'view_mode': 'form,tree,calendar',
            'res_model': 'stock.picking',
            'res_id': new_picking_id,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    def _send_email(self):
        template = self.env.ref('custom_po_creation.email_template_po_return')
        returns = self.picking_id.move_line_ids
        values = {
            'procurement_email': self.env.user.email,
            'email_from': self._get_default_email_from(),
            'receipt_mails': self.picking_id.partner_id.email,
            'returned_items': [f'{r.display_name} ----- {r.quantity}' for r in returns],
        }

        template.with_context(values).send_mail(self.id, force_send=True)

    def _get_default_email_from(self):
        smtp_server = self.env['ir.mail_server'].search([('sequence', '=', 1)], limit=1)
        return smtp_server.smtp_user if smtp_server else 'devodootest54@gmail.com'
