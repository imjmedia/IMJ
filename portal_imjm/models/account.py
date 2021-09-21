# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from itertools import groupby
from odoo.exceptions import UserError,

class AccountMove(models.Model):
    _inherit = "account.move"


    l10n_mx_supplier_cfdi_uuid = fields.Char(string='Fiscal Folio Proveedor', copy=False, readonly=True,)


    def action_create_invoice_from_po(self, order_rec):
        """Create the invoice associated to the PO.
        """
        factura = self.env['account.move'].create({
            'partner_id': order_rec.partner_id.id,
            'purchase_id': order_rec.id,
            'type': 'in_invoice',
            'date': fields.Date.today(),
            'invoice_origin': order_rec.name,
        })
        factura.purchase_vendor_bill_id = order_rec.id
        po_lines = order_rec.order_line - factura.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            fiscal_position = factura.fiscal_position_id
            accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
            new_line = new_lines.create({
                'name': '%s: %s' % (order_rec.name, line.name),
                'move_id': factura.id,
                'currency_id': factura.currency_id.id,
                'purchase_line_id': line.id,
                'date_maturity': factura.invoice_date_due,
                'product_uom_id': line.product_uom.id,
                'product_id': line.product_id.id,
                'price_unit': line.price_unit,
                'quantity': qty,
                'partner_id': factura.commercial_partner_id.id,
                'analytic_account_id': line.account_analytic_id.id,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'tax_ids': [(6, 0, line.taxes_id.ids)],
                'display_type': line.display_type,
                'account_id': accounts['expense'].id,
            })
            new_line._onchange_price_subtotal()
        return factura

    def action_create_invoice_po_v14(self,order):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        #for order in self:

        #order = order.with_company(order.company_id)
        pending_section = None
        # Invoice values.
        invoice_vals = order._prepare_invoice_v14()
        # Invoice line values (keep only necessary sections).
        for line in order.order_line:
            if line.display_type == 'line_section':
                pending_section = line
                continue
            #if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
            if pending_section:
                invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                pending_section = None
            invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
        invoice_vals_list.append(invoice_vals)

        #if not invoice_vals_list:
        #    raise UserError(_('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return moves

    def _prepare_invoice_v14(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': self.partner_ref or '',
            'move_type': move_type,
            'narration': self.notes,
            'currency_id': self.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(partner_invoice_id)).id,
            'payment_reference': self.partner_ref or '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals