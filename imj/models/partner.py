from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string='Tax ID', required=True, help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")

    _sql_constraints = [
        ('vat_uniq', 'unique (vat)', 'El RFC debe ser Unico!')
    ]