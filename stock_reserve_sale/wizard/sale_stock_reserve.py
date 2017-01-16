# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Leonardo Pistone
#    Copyright 2013-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, exceptions


class SaleStockReserve(models.TransientModel):
    _name = 'sale.stock.reserve'

    date_validity = fields.Date(
        "Validity Date",
        help="If a date is given, the reservations will be released "
             "at the end of the validity.")
    note = fields.Text('Notes')

    @api.multi
    def _prepare_stock_reservation(self, line):
        self.ensure_one()
        return {'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': line.product_uom_qty,
                'date_validity': self.date_validity,
                'name': "%s (%s)" % (line.order_id.name, line.name),
                'note': self.note,
                'price_unit': line.price_unit,
                'sale_line_id': line.id,
                }

    @api.multi
    def stock_reserve(self, line_ids):
        self.ensure_one()

        lines = self.env['sale.order.line'].browse(line_ids)
        for line in lines:
            if not line.is_stock_reservable:
                continue
            vals = self._prepare_stock_reservation(line)
            reserv = self.env['stock.reservation'].create(vals)
            reserv.reserve()
        return True

    @api.multi
    def button_reserve(self):
        env = self.env
        self.ensure_one()
        close = {'type': 'ir.actions.act_window_close'}
        active_model = env.context.get('active_model')
        active_ids = env.context.get('active_ids')
        if not (active_model and active_ids):
            return close

        if active_model == 'sale.order':
            sales = env['sale.order'].browse(active_ids)
            line_ids = [line.id for sale in sales for line in sale.order_line]

        if active_model == 'sale.order.line':
            line_ids = active_ids

        self.stock_reserve(line_ids)
        return close
