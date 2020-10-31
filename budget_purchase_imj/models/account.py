

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp





class CrossoveredBudge(models.Model):
    _inherit = "crossovered.budget"

    start_date = fields.Date('Inicio')
    end_date = fields.Date('Fin')

    @api.onchange('start_date','end_date')
    def _onchange_dates(self):
        for budget in self:
            if budget.start_date and budget.end_date:
                days=fields.Date.from_string(budget.end_date) - fields.Date.from_string(budget.start_date)
                for line in budget.crossovered_budget_line:
                    line.duration=days.days


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    amount_purchase = fields.Float(string='Importe Compras')
    qty = fields.Float(string='Cantidad')
    price = fields.Float(string='Precio')
    duration = fields.Integer(strin='Duración', compute='_compute_duration_imj')
    planned_amount = fields.Monetary(
        'Planned Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    


    def _compute_duration_imj(self):
        for line in self:
            if line.crossovered_budget_id.start_date and line.crossovered_budget_id.end_date:
                days=fields.Date.from_string(line.crossovered_budget_id.end_date) - fields.Date.from_string(line.crossovered_budget_id.start_date)
                line.duration=days.days
            else:
                line.duration=0


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

    






