# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class ReportStockForecat(models.Model):
    _name = 'report.stock.kit'
    _auto = False
    """
    Report that shows the manufacturable quantity of the products based on the on hand quantity of bom componants.
    Group by warehouse.
    """

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    qty_available = fields.Float(readonly=True, string="Quantity On Hand")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_stock_kit')
        self._cr.execute(
            """
                CREATE or REPLACE VIEW report_stock_kit AS (
                    SELECT
                        ROW_NUMBER() OVER () AS id,
                        MAIN.prod_id AS product_id,
                        MAIN.tmpl_id AS product_tmpl_id,
                        MAIN.warehouse_id,
                        MIN(MAIN.quantity) as qty_available
                    FROM (
                        SELECT
                            pp.id as prod_id,
                            mbl.product_id as bom_product_id,
                            pt.id as tmpl_id,
                            sl.warehouse_id AS warehouse_id,
                            SUM(sq.quantity/mbl.product_qty)::integer as quantity
                        FROM
                            product_product pp
                        LEFT JOIN
                            product_template pt ON pt.id = pp.product_tmpl_id
                        LEFT JOIN
                            mrp_bom mb ON mb.id = pt.bom_id
                        LEFT JOIN
                            mrp_bom_line mbl ON mbl.bom_id = mb.id AND mbl.to_exclude = False
                        LEFT JOIN
                            mrp_bom_line_product_attribute_value_rel bml_att_rel ON bml_att_rel.mrp_bom_line_id = mbl.id
                        LEFT JOIN
                            product_attribute_value_product_product_rel pa_rel on pa_rel.product_attribute_value_id = bml_att_rel.product_attribute_value_id
                        LEFT JOIN
                            stock_quant sq ON sq.product_id = mbl.product_id OR sq.product_id = pp.id
                        LEFT JOIN
                            stock_location sl ON sl.id = sq.location_id
                        WHERE
                            sl.usage = 'internal' AND
                            pt.bom_id IS NOT NULL AND
                            pa_rel.product_product_id = pp.id
                        GROUP BY
                            pp.id,
                            pt.id,
                            sl.warehouse_id,
                            mbl.product_id
                        UNION ALL
                        SELECT
                            pp.id as prod_id,
                            mbl.product_id as bom_product_id,
                            pt.id as tmpl_id,
                            sl.warehouse_id AS warehouse_id,
                            SUM(sq.quantity/mbl.product_qty)::integer as quantity
                        FROM
                            product_product pp
                        LEFT JOIN
                            product_template pt ON pt.id = pp.product_tmpl_id
                        LEFT JOIN
                            mrp_bom mb ON mb.id = pt.bom_id
                        LEFT JOIN
                            mrp_bom_line mbl ON mbl.bom_id = mb.id AND mbl.to_exclude = False
                        LEFT JOIN
                            stock_quant sq ON sq.product_id = mbl.product_id OR sq.product_id = pp.id
                        LEFT JOIN
                            stock_location sl ON sl.id = sq.location_id
                        WHERE
                            sl.usage = 'internal' AND
                            pt.bom_id IS NOT NULL AND
                            mbl.id NOT IN (select rel.mrp_bom_line_id from mrp_bom_line_product_attribute_value_rel rel)
                        GROUP BY
                            pp.id,
                            pt.id,
                            sl.warehouse_id,
                            mbl.product_id) AS MAIN
                    GROUP BY
                        MAIN.prod_id,
                        MAIN.tmpl_id,
                        MAIN.warehouse_id
            )""")
