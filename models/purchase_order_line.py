from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    @api.constrains('product_id')
    def _check_non_moving_product(self):
        company = self.env.company
        for line in self:
            product_template = line.product_id.product_tmpl_id

            # check non-moving items
            if company.enable_po_validation_on_create and product_template.is_non_moving_product:
                self._validate_non_moving_product(line, product_template)

            # check stock-clearance
            if company.enable_po_validation_on_create and product_template.track_stock_clearance and product_template.track_days:
                self._validate_stock_clearance(line, product_template)

    def _validate_stock_clearance(self, line, product_template):
        qoh = line.product_id.product_variant_id.qty_available
        sold = self._get_sold_quantities(line.product_id.id, product_template.track_days)
        sold_qty = sold.get('sold_qty')
        if not sold_qty:
            raise ValidationError(_(
                f"No sales made so far for [{line.product_id.name}].Stock is available {qoh}"
            ))
        if sold_qty and qoh:
            if sold_qty / (qoh + sold_qty) < 0.5:
                raise ValidationError(_(
                    f"The product [{line.product_id.name}] has not sold at least 50% of the last Stock. Only {sold_qty} of {qoh + sold_qty} has been sold "
                ))

    def _validate_non_moving_product(self, line, product_template):
        non_moving_cutoff_date = datetime.now() - timedelta(days=product_template.non_moving_period_days)
        formatted_date = non_moving_cutoff_date.strftime('%Y-%m-%d')

        self.env.cr.execute("""
                                    SELECT COUNT(*) FROM stock_move
                                    WHERE product_id = %s
                                      AND state = 'done'
                                      AND date::date >= %s
                                """, (line.product_id.id, formatted_date))
        result = self.env.cr.fetchone()
        move_count = result[0] if result else 0

        if move_count == 0:
            raise ValidationError(
                _(f"The product {line.product_id.name} is a non-moving product and cannot be added to a purchase order."
                  )
            )

    def _get_sold_quantities(self, product_id, clearance_days):
        """
        SELECT sum(l. product_uom_qty) qtys  FROM sale_order_line l JOIN sale_order o
        ON l.order_id = o.id  WHERE product_id=36 AND o.state='sale'
        AND o.date_order BETWEEN '2024-07-01' AND '2024-07-31'
        """
        start_date = datetime.now() - timedelta(days=clearance_days)
        max_date = datetime.now() + timedelta(days=1)
        formatted_start_date = start_date.strftime('%Y-%m-%d')
        formatted_max_date = max_date.strftime('%Y-%m-%d')

        # get sold qtys from sale.order
        self.env.cr.execute("""
                 SELECT 
                    SUM(l.product_uom_qty) AS total_sold_quantity
                 FROM sale_order_line l 
                 JOIN sale_order o ON l.order_id=o.id 
                 WHERE l.product_id=%s And o.state='sale' AND o.date_order BETWEEN %s AND %s 
                """, (product_id, formatted_start_date, formatted_max_date))
        sale_res = self.env.cr.fetchone()
        sale_qty = sale_res[0] if sale_res[0] else 0

        # get sold qtys from pos.order
        self.env.cr.execute("""
                         SELECT 
                            SUM(l.qty) AS total_sold_quantity
                         FROM pos_order_line l 
                         JOIN pos_order o ON l.order_id=o.id 
                         WHERE l.product_id=%s And o.state in ('paid') AND o.date_order BETWEEN %s AND %s 
                        """, (product_id, formatted_start_date, formatted_max_date))
        pos_res = self.env.cr.fetchone()
        pos_qty = pos_res[0] if pos_res[0] else 0
        return {
            'sold_qty': pos_qty + sale_qty
        }
