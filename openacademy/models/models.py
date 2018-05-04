# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

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

	_sql_constraints = [
		('name_description_check',
		 'CHECK( name != description)',
		 "The title of the course should not be the description"
		),
		('name_unique',
		 'UNIQUE(name)',
		 "The course title must be unique"
		),
	]

#	def copy(self, default=None):
#		if default is None:
#			default = {}
#		default['name'] = self.name + ' otro'
#		return super(Course, self).copy(default)

	def copy(self, default=None):
		if default is None:
			default = {}
		copied_count = self.search_count([('name', 'ilike', 'Copy of %s%%' % (self.name))])
		if not copied_count:
			new_name = "Copy of %s" % (self.name)
		else:
			new_name = "Copy of %s (%s)" % (self.name, copied_count)
		default['name'] = new_name
		return super(Course, self).copy(default)


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
	@api.onchange('seats','attendee_ids')
	def _verify_valid_seats(self):
		if self.filtered(lambda r: r.seats < 0):
			self.active = False
			return {
				'warning': {
					'title': "Incorrect 'seats' value",
					'message': "The number of available seats may not be negative",
				}
			}
		if self.seats < len(self.attendee_ids):
			self.active = False
			return {
				'warning': {
					'title': "Too many attendees",
					'message': "Increase seats or remove excess attendees",
				}
			}
		self.active = True

	@api.constrains('instructor_id','attendee_ids')
	def _check_instructor_not_in_attendees(self):
		for record in self.filtered('instructor_id'):
			if record.instructor_id in record.attendee_ids:
				raise exceptions.ValidationError("A session's instructor can't be an attendee")
