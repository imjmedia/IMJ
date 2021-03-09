

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductCategory(models.Model):
    _inherit = "product.category"

    cost_edit = fields.Boolean('Modificar Costo', copy=False)


    def write(self, values):
        res = super(ProductCategory, self).write(values)
        if 'cost_edit' in values:
            templates=self.env['product.template']
            ids_tmp=templates.search([('categ_id','=',self.id)])
            ids_tmp.write({'cost_edit':values.get('cost_edit')})

        return res

class ProductTemplate(models.Model):
    _inherit = "product.template"

    cost_edit = fields.Boolean('Modificar Costo', copy=False)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    cost_edit = fields.Boolean(relation='product_id.cost_edit', string='Modificar Costo', copy=False)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.cost_edit=self.product_id.cost_edit
        self._product_id_change()

        self._suggest_quantity()
        self._onchange_quantity()


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval = fields.Boolean('Visto bueno', copy=False)

    def button_confirm(self):
        budget = self.env['crossovered.budget']
        for order in self:
            positivo=False
            id_budget=budget.search([('date_from', '<=', fields.Date.context_today(self)),('date_to', '>=', fields.Date.context_today(self)),('state','=','validate')])
            if id_budget:
                for pline in order.order_line:
                    for p in id_budget:
                        for line in p.crossovered_budget_line:
                            prod_account_id=pline.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)['expense']
                            if (line.analytic_account_id.id==pline.account_analytic_id.id) and (line.account_id.id==prod_account_id.id):
                                positivo=True
                                break
                if not positivo:
                    raise UserError(('No existe linea de presupuesto activo para las lineas de presupuesto:'))


                for pline in order.order_line:
                    for p in id_budget:
                        for line in p.crossovered_budget_line:
                            if line.planned_amount > 0.0:
                                amount_purchase=(line.planned_amount - line.amount_purchase)
                                prod_account_id=pline.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)['expense']
                                if (line.analytic_account_id.id==pline.account_analytic_id.id) and (line.account_id.id==prod_account_id.id):
                                    if pline.price_subtotal > amount_purchase:
                                        raise UserError(('El monto del producto:  "%s" y la Cuenta: "%s" Sobrepasan el presupuesto: "%s" ') % (pline.product_id.name_get()[0][1],line.account_id.name,p.name))
                                    else:
                                        line.write({'amount_purchase':line.amount_purchase + pline.price_subtotal})
            else:
                raise UserError(('No hay presupuesto activo para la fecha:')) 
        super(PurchaseOrder, self).button_confirm() 
        return True
    
    def button_cancel(self):
        budget = self.env['crossovered.budget']
        for order in self:
            if order.state=='purchase':
                id_budget=budget.search([('date_from', '<=', fields.Date.context_today(self)),('date_to', '>=', fields.Date.context_today(self)),('state','=','validate')])
                if id_budget:
                    for pline in order.order_line:
                        for p in id_budget:
                            for line in p.crossovered_budget_line:
                                if line.planned_amount > 0.0:
                                    prod_account_id=pline.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=order.fiscal_position_id)['expense']
                                    if (line.analytic_account_id.id==pline.account_analytic_id.id) and (line.account_id.id==prod_account_id.id):
                                        line.write({'amount_purchase':line.amount_purchase - pline.price_subtotal})
        super(PurchaseOrder, self).button_cancel()



