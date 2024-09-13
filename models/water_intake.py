from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class WaterIntake(models.Model):
    _name = 'water.intake'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Water Intake'
    _rec_name = 'form_seq'

    STATES = {'done': [('readonly', True)]}
    date = fields.Date(default=datetime.today(), string="Date")
    daily_goal = fields.Float(string="Daily Water Intake Goal Litres (L)")
    water_intake_id = fields.One2many('related.water.intake', 'related_water_id')
    progress = fields.Float(compute='_compute_progress', string="Progress (%)", store=True)
    form_seq = fields.Char(string='Water Intake ID', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New Water Intake'))
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('done', 'Done')],
                             default='draft')

    def action_pending(self):
        self.state = 'pending'

    def action_done(self):
        self.state = 'done'

    @api.model
    def create(self, values):
        if values.get('form_seq', _('New Water Intake')) == _('New Water Intake'):
            values['form_seq'] = self.env['ir.sequence'].next_by_code('water.intake') or _(
                'New Water Intake')
            return super(WaterIntake, self).create(values)

    @api.depends('water_intake_id', 'daily_goal')
    def _compute_progress(self):
        for record in self:
            total_intake = sum(record.water_intake_id.mapped('intake'))
            record.progress = (total_intake / record.daily_goal) * 100 if record.daily_goal != 0 else 0

    @api.constrains('water_intake_id', 'daily_goal')
    def _check_daily_goal(self):
        for record in self:
            total_intake = sum(record.water_intake_id.mapped('intake'))
            if total_intake > record.daily_goal:
                raise ValidationError("Daily water intake goal should equal total water quantity.")


class RelatedWaterIntake(models.Model):
    _name = 'related.water.intake'
    _description = 'Water Intake Relation'

    related_water_id = fields.Many2one('water.intake')
    time_taken = fields.Datetime(default=lambda self: fields.datetime.now(), string="Intake Date / Time")
    intake = fields.Float(string="Water Quantity Litres (L)")
    # unit = fields.Selection([('litres','Litres'), ('ml','Milliliters'), ('ounce','Ounce')], string="Unit")
