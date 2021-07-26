# -*- coding: utf-8 -*-
from odoo import fields, models, api,_
from dateutil.relativedelta import relativedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    opinion_sat = fields.Binary(string='Opinion del SAT')
    valid_until = fields.Date(string='Valido hasta')
    estado_opinion = fields.Selection(string='Estado de la opinion', default='invalida',
                                      selection=[('valida', 'Válida'), ('invalida', 'No válida'), ('revision', 'En revisión')])
    opinion_msg_stat = fields.Char(string='Detalle del estado')

    @api.onchange('estado_opinion')
    def _onchange_estado_opinion(self):
        if self.estado_opinion and self.estado_opinion == 'valida':
            self.valid_until = fields.Date.today() + relativedelta(days=90)
            self.opinion_msg_stat = 'Documentación validada con éxito.'