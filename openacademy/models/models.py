# -*- coding: utf-8 -*-

from odoo import models, fields, api

def get_uid(self, *a):
	return self.env.uid


class Course(models.Model):
	_name = 'openacademy.course'

	name = fields.Char(string="Title", required=True)
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
	description = fields.Text()
#	responsible_id = fields.Many2one('res.users', string="Responsible", index=True, ondelete='set null', default=lambda self, *a: self.env.uid)
	responsible_id = fields.Many2one('res.users', string="Responsible", index=True, ondelete='set null', default=get_uid)
	session_ids = fields.One2many('openacademy.session','course_id')
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class Session(models.Model):
	_name = 'openacademy.session'

	name = fields.Char(required=True)
	start_date = fields.Date(default=fields.Date.today)
	datetime_test = fields.Datetime(default=fields.Datetime.now)
	duration = fields.Float(digits=(6,2), help="Duration in days")
	seats = fields.Integer(string="Number of seats")
	instructor_id = fields.Many2one('res.partner',string='Instructor',
					domain=['|',('instructor','=','True'),('category_id.name','ilike','Teacher')])
	course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
	attendee_ids = fields.Many2many('res.partner', string="Attendees")
	taken_seats = fields.Float(compute='_taken_seats')
	active = fields.Boolean(default=True)

	@api.depends('seats','attendee_ids')
	def _taken_seats(self):
		for record in self.filtered(lambda r: r.seats):
			record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats

#	@api.depends('seats','attendee_ids')
#	def _taken_seats(self):
#		#import pdb; pdb.set_trace()
#		for record in self:
#			if not record.seats:
#				record.taken_seats = 0
#			else:
#				record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
