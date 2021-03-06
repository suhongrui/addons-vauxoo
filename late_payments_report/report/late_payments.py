# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Luis Escobar <luis@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

import time


from openerp.report import report_sxw


class Late_payments(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Late_payments, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'adr_get': self._adr_get,
            'getLines': self._lines_get,
            'tel_get': self._tel_get,
            'message': self._message,
        })
        self.context = context

    def _adr_get(self, partner, type):
        res = []
        res_partner = pooler.get_pool(self.cr.dbname).get('res.partner')
        res_partner_address = pooler.get_pool(
            self.cr.dbname).get('res.partner.address')
        addresses = res_partner.address_get(
            self.cr, self.uid, [partner.id], [type])
        adr_id = addresses and addresses[type] or False
        result = {
            'name': False,
            'street': False,
            'city': False,
            'zip': False,
            'country_id': False,
        }
        if adr_id:
            result = res_partner_address.read(self.cr, self.uid, [
                                              adr_id], context=self.context.copy())
            result[0]['country_id'] = result[0][
                'country_id'] and result[0]['country_id'][1] or False
            return result

        res.append(result)
        return res

    def _tel_get(self, partner):
        if not partner:
            return False
        res_partner_address = pooler.get_pool(
            self.cr.dbname).get('res.partner.address')
        res_partner = pooler.get_pool(self.cr.dbname).get('res.partner')
        addresses = res_partner.address_get(
            self.cr, self.uid, [partner.id], ['invoice'])
        adr_id = addresses and addresses['invoice'] or False
        if adr_id:
            adr = res_partner_address.read(self.cr, self.uid, [adr_id])[0]
            return adr['phone']
        else:
            return partner.address and partner.address[0].phone or False
        return False

    def _lines_get(self, partner):
        moveline_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        movelines = moveline_obj.search(self.cr, self.uid,
                                        [('partner_id', '=', partner.id),
                                       ('account_id.type', 'in', [
                                        'receivable', 'payable']),
                                            ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(self.cr, self.uid, movelines)
        return movelines

    def _message(self, obj, company):
        company_pool = pooler.get_pool(self.cr.dbname).get('res.company')
        message = company_pool.browse(self.cr, self.uid, company.id, {
                                      'lang': obj.lang}).overdue_msg
        return message

report_sxw.report_sxw('report.account.late.payments.l10n.ve', 'res.partner',
                      'addons/late_payments_report/report/late_payments.rml', parser=Late_payments)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
