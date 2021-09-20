# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class purchase_order(models.Model):
    _inherit = "purchase.order"

    ultimo_pdf = fields.Binary(string='Último .pdf', help='Último archivo .pdf cargado desde el portal por el vendedor')
    ultimo_xml = fields.Binary(string='Último .xml', help='Último archivo .xml cargado desde el portal por el vendedor')
    pdf_xml_filenames = fields.Char(string='Nombres del archivo', help='sin extensión')

