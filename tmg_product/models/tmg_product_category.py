from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, \
    ValidationError, Warning


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_brand = fields.Boolean(string="Brand Level Category", default=False)
    brand = fields.Many2one('product.category', string="Brand")

    @api.multi
    @api.onchange('is_brand')
    def ensure_only_brand(self):
        #Check to make sure that it is the only Brand
        parents = self.get_hierarchy(self.id)
        for p in parents:
            if p.is_brand:
                raise Warning('Category ' + p.name + ' is already set as Brand in hierarchy.')

    #Returns array of child Categories
    def get_children(self, category_id):
        category = self.env['product.category'].browse(category_id)
        if not category:
            return []
        master_children = []
        current_children = []
        current_children.append(self)
        has_children = True
        while has_children:
            proc_children = []
            for child in current_children:
                children = self.env['product.category'].search([('parent_id', '=', self.id)])
                for r in children:
                    r = self.env['product.category'].browse(r)
                    proc_children.append(r)
            current_children = []
            if len(proc_children) == 0:
                has_children = False
            else:
                current_children.append(proc_children)
        master_children.append(current_children)
        return master_children

    #Returns array of category hierarchy
    def get_hierarchy(self, category_id):
        category = self.env['product.category'].browse(category_id)
        if not category:
            return []
        parents = []
        final_level = False
        if not category.parent_id:
            return []
        while not final_level:
            if not category.parent_id:
                final_level = True
            else:
                parents.append(category.parent_id)
                category = category.parent_id
        return parents

    @api.multi
    @api.depends('is_brand')
    def set_child_brands(self):
        children = self.get_children(self.id)
        if children:
            for c in children:
                if self.is_brand:
                    c.brand = self
                else:
                    c.brand = False

    @api.multi
    @api.depends('parent_id')
    def set_current_brand(self):
        parents = self.get_hierarchy(self.id)
        for p in parents:
            if p.is_brand:
                self.brand = p

