# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ResPartner(models.Model):
    _inherit = 'res.partner'

    opinion_sat = fields.Binary(string="Opinion del SAT")
    valid_until = fields.Date(string='Valido hasta')