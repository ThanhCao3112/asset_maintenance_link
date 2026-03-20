# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    account_asset_category_id = fields.Many2one(
        'account.asset.category',
        string='Accounting Asset Category',
        help='Used to automatically populate the correct asset category when generating an asset from equipment.'
    )

    def action_create_accounting_category(self):
        self.ensure_one()
        return {
            'name': _('Create Accounting Category'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.category',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_name': self.name,
                'default_type': 'purchase',
                'maintenance_category_id': self.id,
            }
        }

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    account_asset_id = fields.Many2one(
        'account.asset.asset',
        string='Accounting Asset',
        copy=False,
        help='Linked financial asset for depreciation tracking.'
    )

    @api.constrains('company_id', 'account_asset_id')
    def _check_company_match(self):
        for record in self:
            if record.account_asset_id and record.company_id and record.account_asset_id.company_id:
                if record.company_id != record.account_asset_id.company_id:
                    raise ValidationError(_('The equipment and the linked accounting asset must belong to the same company.'))

    def write(self, vals):
        # Handle bi-directional name sync
        res = super(MaintenanceEquipment, self).write(vals)
        
        # Check archive action
        if 'active' in vals and not vals['active']:
            for equipment in self.filtered('account_asset_id'):
                equipment.account_asset_id.message_post(
                    body=_("Warning: The linked maintenance equipment '%s' has been archived/scrapped. Please review if this financial asset should be disposed.") % equipment.name
                )
                
        if 'name' in vals and not self.env.context.get('skip_asset_name_sync'):
            for equipment in self.filtered('account_asset_id'):
                equipment.account_asset_id.sudo().write({'name': vals['name']})
                
        return res

    def unlink(self):
        for record in self:
            if record.account_asset_id:
                raise ValidationError(_('You cannot delete a maintenance equipment that is linked to an accounting asset. Please archive it instead or remove the link first.'))
        return super(MaintenanceEquipment, self).unlink()

    def action_generate_asset(self):
        self.ensure_one()
        if self.account_asset_id:
            raise ValidationError(_('This equipment is already linked to an accounting asset.'))
            
        asset_vals = {
            'name': self.name,
            'value': self.cost or 0.0,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'company_id': self.company_id.id or self.env.company.id,
            'date': self.assign_date or fields.Date.today(),
            'equipment_id': self.id,
            'category_id': self.category_id.account_asset_category_id.id if self.category_id and self.category_id.account_asset_category_id else False,
        }
        
        if not asset_vals['category_id']:
            raise ValidationError(_("Please select an Asset Category mapping on the equipment's category, or manually create the asset if you don't use categories."))
            
        new_asset = self.env['account.asset.asset'].sudo().create(asset_vals)
        self.write({'account_asset_id': new_asset.id})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.asset',
            'res_id': new_asset.id,
            'view_mode': 'form',
            'target': 'current',
        }
