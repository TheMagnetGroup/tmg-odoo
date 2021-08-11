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
        if self.parent_id:
            parents = self.get_hierarchy(self.parent_id.id)
            for p in parents:
                if p.is_brand:
                    raise Warning('Parent category ' + p.name + ' is already set as Brand in hierarchy.')


    #Returns array of child Categories
    def get_children(self, category_id):
        category = self.env['product.category'].browse(category_id)
        if not category:
            return []
        master_children = []
        current_children = []
        prox = self.env['product.category'].browse(category_id)
        current_children.append(category)

        has_children = True
        while has_children:
            proc_children = []
            for child in current_children:
                varID = 0
                if isinstance(child.id, int):
                    varID = child.id
                else:
                    varID = child.id.id

                if child.child_id:
                    children = child.child_id.ids
                else:
                    children = self.env['product.category'].search([('parent_id', '=', varID)])
                for r in children:
                    s = self.env['product.category'].browse(r)
                    proc_children.append(s)
                    master_children.append(r)
            current_children = proc_children
            if len(proc_children) == 0:
                has_children = False
            # else:
            #     master_children = master_children + proc_children
        # master_children = master_children + current_children
        return master_children

    #Returns array of category hierarchy
    def get_hierarchy(self, parent_id):
        category = self.env['product.category'].browse(parent_id)
        if not category:
            return []
        parents = [category]
        final_level = False
        if not category.parent_id:
            return parents
        while not final_level:
            if not category.parent_id:
                final_level = True
            else:
                parents.append(category.parent_id)
                category = category.parent_id
        return parents

    @api.multi
    @api.onchange('is_brand')
    def set_child_brands(self):
        children = self.get_children(self._origin.id)
        if children:
            output = []
            child_objs = self.env['product.category'].browse(children)
            if self.is_brand:
                child_objs.write({"brand": self._origin.id})
            else:
                child_objs.write({"brand": False})
            # for c in children:
            #     if isinstance(c.id, int):
            #         output.append(c)
            #     else:
            #         output.append(c.id)
            #     if self.is_brand:
            #         output.write({"brand": self._origin.id})
            #     else:
            #         output.write({"brand": False})

    @api.multi
    @api.onchange('parent_id')
    def set_current_brand(self):
        if self.parent_id:
            parents = self.get_hierarchy(self.parent_id.id)
            set_parent = False
            for p in parents:
                if p.is_brand:
                    self.brand = p
                    set_parent = True
            if not set_parent:
                self.brand = False
        else:
            self.brand = False

