from email.policy import default
from operator import index

from odoo import models,fields,api
from datetime import timedelta

from odoo.exceptions import ValidationError


class CustomerComplaint(models.Model):
    _name = 'customer.complaint'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=1,tracking=1)
    active = fields.Boolean(default=1)
    creation_date = fields.Date(default=fields.Date.context_today,tracking=1)
    reference = fields.Char(default="",readonly=1,tracking=1)
    state = fields.Selection([
        ('draft','Draft'),
        ('submitted','Submitted'),
        ('refused','Refused'),
        ('approved','Approved')
    ],default='draft',string='Status')
    comment = fields.Html(string='Notes',placeholder='Internal Notes',tracking=1)
    complainant = fields.Char(string='Company Name Complaining',tracking=1)
    customer_name = fields.Char(string='Customer Name',tracking=1)
    complaint_date = fields.Date(string='Complaint Date',tracking=1)
    complaint_description = fields.Text(tracking=1)
    proposed_action = fields.Text(string='Action',tracking=1)
    proposed_completion_date = fields.Date(tracking=1)
    result = fields.Text(string='Proposed Action Result',tracking=1)
    actual_completion_date = fields.Date(tracking=1)
    actual_completion_period = fields.Integer(string='Actual Completion Period (Days)',compute='_compute_actual_completion_period',tracking=1)

    attachment_ids = fields.Many2many('ir.attachment','res_id',string='Attachments',domain=[('res_model', '=', 'customer.complaint')])
    employee_id = fields.Many2one('hr.employee',string='Employee',required=1,index=1,
                                  default=lambda self:self.env['hr.employee'].search([('user_id', '=', self.env.uid)]),limit=1,
                                  domain=lambda self:[('company_id', '=', self.env.company.id)])
    job_id = fields.Many2one('hr.job',string='Job Position',related='employee_id.job_id')
    department_id = fields.Many2one('hr.department',string='Job Position',related='employee_id.department_id')
    company_id = fields.Many2one('res.company',string='Company',
                                 default=lambda self:self._default_company())
    logicom_company_id = fields.Many2one('res.company', string='Logicom Company')
    assigned_manager_id = fields.Many2one('hr.employee', string='Assigned Manager')

    responsible_id = fields.Many2one('hr.employee',string='Responsible Person')
    task_ids = fields.One2many('project.task',)



    @api.model
    def _default_company(self):
        employee = self.env['hr.employee'].search([('user_id','=',self.env.uid)],limit=1)
        return employee.company_id.id if employee else False

    @api.constrains('employee_id','company_id')
    def _check_employee_company(self):
        for rec in self:
            if rec.employee_id and rec.company_id and rec.employee_id.company_id != rec.company_id:
                raise ValidationError ("The company of the selected employee must match the selected company.")


    @api.constrains('state','responsible_id','result','actual_completion_date')
    def _check_state(self):
        for rec in self:
            if rec.state == 'approved' and not rec.responsible_id:
                raise ValidationError ("The 'Responsible Person' field is mandatory when converting the state to 'To Approve'.")
            elif rec.state == 'approved' and not rec.result:
                raise  ValidationError ("The 'Proposed Action Result' field is mandatory when converting the state to 'To Approve'.")
            elif rec.state == 'approved' and not rec.actual_completion_date:
                raise ValidationError ("The 'Actual Completion Date' field is mandatory when converting the state to 'To Approve'.")


    @api.model
    def create(self,vals):
        res = super(CustomerComplaint,self).create(vals)
        if res.reference == '':
            res.reference = self.env['ir.sequence'].next_by_code('customer_complaint_seq')
        return res

    @api.depends('actual_completion_date','creation_date')
    def _compute_actual_completion_period(self):
        for rec in self:
            if rec.creation_date and rec.actual_completion_date:
                delta = rec.actual_completion_date - rec.creation_date
                rec.actual_completion_period = delta.days
            else:rec.actual_completion_period = 0

    def action_confirm(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_mark_as_draft(self):
        self.write({'state': 'draft'})

