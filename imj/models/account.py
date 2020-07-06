

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # Columns Section
    compartido = fields.Boolean(
        string='Compartido')

    listado = fields.fields.Selection(
        selection=[('local','Local'),
                    ('foraneo','Foraneo'),
                ],
        string="Listado",
    )


