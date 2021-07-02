# -*- coding: utf-8 -*-
import base64

from odoo import http, fields
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.mimetypes import guess_mimetype
from dateutil.relativedelta import relativedelta

File_Type = ['application/pdf', 'image/jpeg', 'image/png']  # allowed file type

CustomerPortal.OPTIONAL_BILLING_FIELDS.append('valid_until',)
CustomerPortal.OPTIONAL_BILLING_FIELDS.append('partner')
CustomerPortal.OPTIONAL_BILLING_FIELDS.append('attachment')

class CustomerPortal(CustomerPortal):


    @http.route(['/upload/opinion/'], type='http', auth="user", method="post", csrf=False, website=True)
    def upload_opinion_sat(self, **post):
        partner_id_int = post.get('partner') and int(post.get('partner')) or False
        partner_id = request.env['res.partner'].browse(partner_id_int)
        if post.get('attachment', False):
            file = post.get('attachment')
            attachment = file.read()
            mimetype = guess_mimetype(base64.b64decode(base64.encodebytes(attachment)))
            if mimetype in File_Type:
                partner_id.write({'opinion_sat': base64.encodebytes(attachment), 'valid_until': fields.Date.today() + relativedelta(days=90)})

        return request.redirect('/my/account')
