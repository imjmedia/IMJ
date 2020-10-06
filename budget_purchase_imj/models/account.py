

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp





class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    amount_purchase = fields.Float(string='Importe Compras')

    def _compute_purchase(self):
        for line in self:
                line.amount_purchase = 0.00

    






