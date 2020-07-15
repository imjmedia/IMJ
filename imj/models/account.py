

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # Columns Section
    compartido = fields.Boolean(
        string='Compartido')

    listado = fields.Selection(
        selection=[('local','Local'),
                    ('foraneo','Foraneo'),
                ],
        string="Listado",
    )


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    
    def _compute_percentage(self):
        for line in self:
            if line.practical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
            else:
                line.percentage = 0.00