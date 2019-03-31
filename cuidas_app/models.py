from datetime import datetime
from cuidas_app import db, login_manager
from flask_login import UserMixin
from bson import ObjectId
from enum import Enum
import calendar

@login_manager.user_loader
def load_user(user_id):
	return User.get_by_id(user_id)

class User(UserMixin):
	def __init__(self, id, email, hash, active=True):
		self.id = str(id)
		self.email = email
		self.hash = hash
		self.active = active

	def get_id(self): 
		return self.id

	@staticmethod
	def get_by_id(user_id):
		user = db.users.find_one({
			'_id': ObjectId(user_id)
		})
		if(user):
			return User(user['_id'], user['email'], user['hash'])
		return None

	@staticmethod
	def get_by_email(email):
		user = db.users.find_one({
			'email': email
		})
		if(user):
			return User(user['_id'], user['email'], user['hash'])
		return None

class ScheduleStatus(Enum):
	AVAILABLE = 1
	ASSIGNED = 2
	UNAVAILABLE = 3

class Schedule():
	def __init__(self, hour, minute, status = ScheduleStatus.UNAVAILABLE):
		self.hour = hour
		self.minute = minute
		self.status = status
		self.name = None
		self.email = None
		self.phone = None

	def set_appointment(name, email, phone):
		self.name = name
		self.email = email
		self.phone = phone

	def is_available(self):
		return self.status == ScheduleStatus.AVAILABLE

	def is_assigned(self):
		return self.status == ScheduleStatus.ASSIGNED

	def time_str(self):
		return str(self.hour).zfill(2) + ':' + str(self.minute).zfill(2)

class CalendarDay():
	# Define o começo e fim dos dias
	day_start_time = 8
	day_end_time = 18

	def __init__(self, year, month, day):
		self.year = year
		self.month = month
		self.day = day
		self.schedules = [Schedule(h//2, h%2*30) for h in range(self.day_start_time * 2, self.day_end_time * 2)]

	@staticmethod
	def get_calendar_month(year, month):
		"""Retorna uma lista de objetos dia correspondentes a um mês."""

		day_count = calendar.monthrange(year, month)[1]
		day_list = list(db.calendar_day.find({
				'year': year,
				'month': month
			}))
		day_objects = [CalendarDay.instantiate_from_json(day_json, False) for day_json in day_list]
		for day in range(1, day_count+1):
			if(not any(day_json['day'] == day for day_json in day_list)):
				day_objects.append(CalendarDay(year, month, day))

		day_objects.sort(key=lambda x: x.day)
		return day_objects

	@staticmethod
	def get_calendar_day(year, month, day, instantiate_names=False):
		day_json = db.calendar_day.find_one({
				'year': year,
				'month': month,
				'day': day
			})
		if(day_json):
			return CalendarDay.instantiate_from_json(day_json, instantiate_names)
		else:
			return CalendarDay(year, month, day)

	@staticmethod
	def instantiate_from_json(json, instantiate_names=False):
		day_obj = CalendarDay(json['year'], json['month'], json['day'])
		for sc in day_obj.schedules:
			if(str(sc.hour).zfill(2) + str(sc.minute).zfill(2) in json['schedules']):
				sc_data = json['schedules'][str(sc.hour).zfill(2) + str(sc.minute).zfill(2)]
				sc.status = ScheduleStatus(sc_data['status'])
				if(instantiate_names):
					sc.name = sc_data['name']
					sc.email = sc_data['email']
					sc.phone = sc_data['phone']
		return day_obj

	def save(self):
		day_json = {
			'year': self.year,
			'month': self.month,
			'day': self.day,
			'schedules': {}
		}
		for schedule in self.schedules:
			day_json['schedules'].update({
				str(schedule.hour).zfill(2) + str(schedule.minute).zfill(2): {
					'status': schedule.status.value,
					'name': schedule.name,
					'email': schedule.email,
					'phone': schedule.phone
				}
			})
		db.calendar_day.update({
			'year': self.year,
			'month': self.month,
			'day': self.day
		} , { '$set' : day_json} , True)

	def is_available(self):
		return any(s.status == ScheduleStatus.AVAILABLE for s in self.schedules)

	def is_assigned(self):
		return not self.is_available() and any(s.status == ScheduleStatus.ASSIGNED for s in self.schedules)

	def date_str(self):
		return str(self.day).zfill(2) + '/' + str(self.month).zfill(2) + '/' + str(self.year).zfill(4)
