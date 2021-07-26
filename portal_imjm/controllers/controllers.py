# -*- coding: utf-8 -*-
import base64

from odoo import http, fields
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.mimetypes import guess_mimetype

File_Type = ['application/pdf']  # allowed file type

CustomerPortal.OPTIONAL_BILLING_FIELDS.append('valid_until',)
CustomerPortal.OPTIONAL_BILLING_FIELDS.append('partner')
CustomerPortal.OPTIONAL_BILLING_FIELDS.append('attachment')

class CustomerPortal(CustomerPortal):


    @http.route(['/upload/opinion/'], type='http', auth="user", method="post", csrf=False, website=True)
    def upload_opinion_sat(self, **post):
        partner_id_int = post.get('partner') and int(post.get('partner')) or False
        partner_id = request.env['res.partner'].browse(partner_id_int)
        select_value = dict(request.env['res.partner']._fields['estado_opinion'].selection)
        if post.get('attachment', False):
            file = post.get('attachment')
            attachment = file.read()
            mimetype = guess_mimetype(base64.b64decode(base64.encodebytes(attachment)))
            if mimetype in File_Type:
                partner_id.sudo(True).write({'opinion_sat': base64.encodebytes(attachment), 'estado_opinion': 'revision'})
            else:
                return request.render('portal_imjm.portal_imjm_template_partner', {'error':{'opinion_msg_stat': 'Archivo no valido'},
                                                                                   'partner': partner_id,
                                                                                   'estado_opinion': 'Su archivo no pudo ser enviado! Motivo:',
                                                                                   'opinion_msg_stat': 'El archivo no se identifico como .PDF válido'})

        return request.render('portal_imjm.portal_imjm_template_partner', {'error':{'partner': 'Correcto'},
                                                                           'partner': partner_id,
                                                                           'opinion_msg_stat': 'El archivo fue subido correctamente.',
                                                                           'estado_opinion': select_value.get(partner_id.estado_opinion) or 'En revisión',
                                                                           'valid_until': partner_id.valid_until or 'Fecha: por definir'})