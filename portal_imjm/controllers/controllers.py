# -*- coding: utf-8 -*-
import base64

from odoo import http, fields
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from lxml import objectify
from dateutil.relativedelta import relativedelta
from datetime import datetime as DT

File_Type = ['application/pdf']  # allowed file type
File_xml_type = ['image/svg+xml']  # tipo xml

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

    #funcion para subir xmls y pdfs de factura
    @http.route(['/upload/archivos_factura/'], type='http', auth="user", method="post", csrf=False, website=True)
    def upload_archivos_factura(self, orden_id=None, access_token=None, **post):
        order_id_int = orden_id and int(orden_id) or None
        order_sudo = request.env['purchase.order'].browse(order_id_int)
        if not order_id_int:
            #lo ideal seria que retornara con return request.redirect(order_sudo.get_portal_url()) #pero al no tener order_id, truena
            return request.redirect('/my/purchase')
        errores = ''
        validacion_partner = self.validar_partner_con_sat(order_sudo.partner_id)
        if validacion_partner:
            errores += 'Error en proveedor! ' + validacion_partner
        values = self._purchase_order_get_page_view_values(order_sudo, access_token, **post)
        para_escribir = {}
        if post.get('adjunto_pdf', False) and post.get('adjunto_xml', False):
            file = post.get('adjunto_pdf')
            attachment = file.read()
            mimetype = guess_mimetype(base64.b64decode(base64.encodebytes(attachment)))
            if mimetype in File_Type:
                para_escribir['ultimo_pdf'] = base64.encodebytes(attachment)
            else:
                errores += 'Error de usuario! El archivo .pdf no es un archivo .pdf válido.'
            #fin analisis de pdf, comienza xml
            file = post.get('adjunto_xml')
            attachment = file.read()
            mimetype = guess_mimetype(base64.b64decode(base64.encodebytes(attachment)))
            if mimetype in File_xml_type:
                validacion = self.validar_xml_portal(attachment, order_sudo)
                if validacion[0]:
                    errores += 'Error en xml! ' + validacion[1]
                else:
                    para_escribir['ultimo_xml'] = base64.encodebytes(attachment)
            else:
                errores += 'Error de usuario! El archivo .xml no es un archivo .xml válido.'
        else:
            errores += 'Error de usuario! Ambos archivos son requeridos al adjuntar.'
        #parte final
        if not errores:
            #if order_sudo.invoice_status == 'no':
            #    values['upload_status_msg'] = 'Error de usuario! El pedido de compra aún no está listo para ser facturado.'
            if order_sudo.invoice_status == 'invoiced':
                values['upload_status_msg'] = 'Error de usuario! El pedido de compra ya cuenta con una factura activa previa.'
            else:
                #new_inv_dict = order_sudo.sudo(True).action_create_invoice()
                new_inv = request.env['account.move'].action_create_invoice_from_po
                #if new_inv_dict:
                if new_inv:
                    #new_inv = request.env['account.move'].sudo(True).browse(new_inv_dict['res_id'])
                    new_inv.l10n_mx_edi_cfdi_uuid = validacion[1]
                    new_inv.date = validacion[2]
                    new_inv.invoice_date = validacion[2]
                    request.env['ir.attachment'].sudo().create(
                        {
                            'name': validacion[3] + '.xml',
                            'datas': para_escribir['ultimo_xml'],
                            'res_model': request.env['account.move']._name,
                            'res_id': new_inv.id,
                            'type': 'binary'
                        })
                    request.env['ir.attachment'].sudo().create(
                        {
                            'name': validacion[3] + '.pdf',
                            'datas': para_escribir['ultimo_pdf'],
                            'res_model': request.env['account.move']._name,
                            'res_id': new_inv.id,
                            'type': 'binary'
                        })
                values['upload_status_msg'] = 'Correcto'
        else:
            values['upload_status_msg'] = errores
        return request.render('portal_imjm.portal_imjm_template_purchase_order_form', values)

    def get_node(self, cfdi_node, attribute, namespaces):
        if hasattr(cfdi_node, 'Complemento'):
            node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
            return node[0] if node else None
        else:
            return None

    def validar_xml_portal(self, arch_xml, purch_order_rec):
        try:
            xml_tree = objectify.fromstring(arch_xml)
        except:
            return (True, 'El archivo xml no tiene una estructura válida.')
        if hasattr(xml_tree, 'Emisor') and hasattr(xml_tree, 'Receptor'):
            rfc_emisor = xml_tree.Emisor.attrib['Rfc'].upper()
            rfc_receptor = xml_tree.Receptor.attrib['Rfc'].upper()
            if purch_order_rec.partner_id.vat and (purch_order_rec.partner_id.vat.upper() != rfc_emisor):
                return (True, 'El RFC del proveedor del xml no coincide con el del sistema. (%s vs %s)'%(rfc_emisor, purch_order_rec.partner_id.vat))
            if purch_order_rec.company_id.vat.upper() != rfc_receptor:
                return (True, 'El RFC del receptor del xml no coincide con el del sistema. (%s vs %s)'%(rfc_receptor, purch_order_rec.company_id.vat))
        else:
            return (True, 'El archivo xml no contiene los nodos de emisor y receptor.')
        #termina analisis de rfcs, continua analisis de monto
        monto_xml = float(xml_tree.attrib['Total'])
        monto_orden = purch_order_rec.amount_total
        if monto_orden != monto_xml:
            return (True, 'El monto del xml no coincide con el total de la orden de compra. (%s vs %s)' % (monto_xml, monto_orden))
        fecha_factura = DT.strptime(xml_tree.attrib['Fecha'][:10], '%Y-%m-%d')
        nombre_arch = xml_tree.attrib['Serie'] + xml_tree.attrib['Folio']
        #comienza chequeo de existencia del uuid
        acc_move_obj = request.env['account.move']
        tfd_node = self.get_node(xml_tree, 'tfd:TimbreFiscalDigital[1]', {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},)
        uuid_factura = tfd_node.attrib['UUID']
        facturas_cargadas = acc_move_obj.search([('l10n_mx_supplier_cfdi_uuid', '=', uuid_factura), ('type', '=', 'in_invoice')])
        if facturas_cargadas:
            for factura in facturas_cargadas:
                return (True, 'El UUID %s ya fue cargado en la factura %s.' % (uuid_factura, factura.name))
        return (False, uuid_factura, fecha_factura, nombre_arch)

    def validar_partner_con_sat(self, partner):
        fecha_validez = partner.valid_until
        if not fecha_validez:
            return 'Por favor cargue el documento de la Opinion del SAT en el menú "Mi cuenta" antes de intentar subir facturas.'
        fecha_hoy = fields.date.today()
        if (fecha_validez - fecha_hoy).days < 1:
            return 'La opinión del SAT del proveedor ha expirado: tiene más de 90 días.'
        if partner.estado_opinion not in ['valida']:
            return 'La opinión del SAT del proveedor no es válida.'
        # validar que el RFC del proveedor no esté en la lista negra del sat. ##Hecho en modulo aparte
        pagos_obj = request.env['account.payment']
        fecha_limite = fields.Date.today() - relativedelta(days=30)
        pagos_sin_rep = pagos_obj.search(
            [('payment_date', '<', fecha_limite.strftime(DF)), ('partner_id', '=', partner.id),
             ('state', '=', 'posted'), ('partner_type', '=', 'supplier')])
        for pago in pagos_sin_rep:
            return 'El proveedor tiene complementos de pago sin subir con mas de 30 días de emisión. (%s)'%pago.ref
        return None