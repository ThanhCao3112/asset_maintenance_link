# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    auto_create_equipment = fields.Boolean(
        string='Auto-create Maintenance Equipment',
        help='If checked, validating an asset in this category will automatically generate a maintenance equipment record.'
    )

    @api.model_create_multi
    def create(self, vals_list):
        categories = super(AccountAssetCategory, self).create(vals_list)
        maintenance_category_id = self.env.context.get('maintenance_category_id')
        if maintenance_category_id:
            m_cat = self.env['maintenance.equipment.category'].browse(maintenance_category_id)
            if m_cat.exists() and categories:
                m_cat.account_asset_category_id = categories[0].id
        return categories

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Maintenance Equipment',
        copy=False,
        help='Linked physical equipment for maintenance tracking.'
    )

    def validate(self):
        res = super(AccountAssetAsset, self).validate()
        for asset in self:
            if asset.category_id.auto_create_equipment and not asset.equipment_id:
                # Prepare cost in company currency
                company = asset.company_id or self.env.company
                if asset.currency_id and asset.currency_id != company.currency_id:
                    cost_company_currency = asset.currency_id._convert(
                        asset.value,
                        company.currency_id,
                        company,
                        asset.date or fields.Date.today()
                    )
                else:
                    cost_company_currency = asset.value

                equipment_vals = {
                    'name': asset.name,
                    'cost': cost_company_currency,
                    'partner_id': asset.partner_id.id if asset.partner_id else False,
                    'assign_date': asset.date,
                    'company_id': asset.company_id.id,
                    'account_asset_id': asset.id,
                }
                
                # Link category if mapped
                # We need to find the maintenance category that maps to this asset category
                maintenance_category = self.env['maintenance.equipment.category'].search([
                    ('account_asset_category_id', '=', asset.category_id.id)
                ], limit=1)
                
                if maintenance_category:
                    equipment_vals['category_id'] = maintenance_category.id
                    
                new_equipment = self.env['maintenance.equipment'].sudo().create(equipment_vals)
                asset.write({'equipment_id': new_equipment.id})
                
        return res

    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        for asset in self.filtered('equipment_id'):
            equipment_update_vals = {}
            if 'name' in vals:
                equipment_update_vals['name'] = vals['name']
            if 'value' in vals:
                company = asset.company_id or self.env.company
                if asset.currency_id and asset.currency_id != company.currency_id:
                    cost_company_currency = asset.currency_id._convert(
                        asset.value,
                        company.currency_id,
                        company,
                        asset.date or fields.Date.today()
                    )
                else:
                    cost_company_currency = asset.value
                equipment_update_vals['cost'] = cost_company_currency
                
            if equipment_update_vals:
                # Avoid infinite recursion if bi-directional name sync
                asset.equipment_id.with_context(skip_asset_name_sync=True).sudo().write(equipment_update_vals)
        return res
