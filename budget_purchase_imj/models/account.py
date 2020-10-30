

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp





class CrossoveredBudge(models.Model):
    _inherit = "crossovered.budget"

    start_date = fields.Date('Inicio')
    end_date = fields.Date('Fin')

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    amount_purchase = fields.Float(string='Importe Compras')
    qty = fields.Float(string='Cantidad')
    price = fields.Float(string='Precio')
    duration = fields.Float(strin='Duración')
    planned_amount = fields.Monetary(
        'Planned Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    
    def _compute_amount_imj(self):
        for line in self:
            if line.qty and line.price and line.duration:
                line.planned_amount = line.qty * line.price * line.duration
            else:
                line.planned_amount = 0

    @api.onchange('qty','price','duration')
    def _onchange_planned(self):
        for line in self:
            if line.qty and line.price and line.duration:
                line.planned_amount = line.qty * line.price * line.duration
            else:
                line.planned_amount = 0

    def _compute_purchase(self):
        for line in self:
                line.amount_purchase = 0.00

    






