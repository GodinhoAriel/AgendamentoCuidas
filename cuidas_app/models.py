from datetime import datetime
from cuidas_app import db, login_manager
from flask_login import UserMixin
from bson import ObjectId
from enum import Enum

@login_manager.user_loader
def load_user(user_id):
	user = db.users.find_one({
		'_id': ObjectId(user_id)
	})
	if(user):
		return User(user['_id'], user['email'])

	return None

class User(UserMixin):
	def __init__(self, id, email=None, active=True):
		self.id = str(id)
		self.email = email
		self.active = active

	def get_id(self): 
		return self.id

class ScheduleStatus(Enum):
	AVAILABLE = 1
	ASSIGNED = 2
	UNAVAILABLE = 3

class Schedule():
	def __init__(self, hour, minute, status = ScheduleStatus.UNAVAILABLE):
		self.hour = hour
		self.minute = minute
		self.status = status

	def set_appointment(name, email, phone):
		self.name = name
		self.email = email
		self.phone = phone

	def available(self):
		return self.status == ScheduleStatus.AVAILABLE

	def assigned(self):
		return self.status == ScheduleStatus.ASSIGNED

	def time_str(self):
		return str(self.hour).zfill(2) + ':' + str(self.minute).zfill(2)


class CalendarDay():

	def __init__(self, year, month, day):
		self.year = year
		self.month = month
		self.day = day
		self.schedules = [Schedule(h//2, h%2*30) for h in range(12, 44)]

	@staticmethod
	def instantiate_from_json(json):
		day_obj = CalendarDay(json['year'], json['month'], json['day'])
		for sc in day_obj.schedules:
			if(str(sc.hour).zfill(2) + str(sc.minute).zfill(2) in json['schedules']):
				sc_data = json['schedules'][str(sc.hour).zfill(2) + str(sc.minute).zfill(2)]
				sc.status = ScheduleStatus(sc_data['status'])
				sc.name = sc_data['name']
				sc.email = sc_data['email']
				sc.phone = sc_data['phone']
		return day_obj

	def instantiate_from_json_without_names(json):
		day_obj = CalendarDay(json['year'], json['month'], json['day'])
		for sc in day_obj.schedules:
			if(str(sc.hour).zfill(2) + str(sc.minute).zfill(2) in json['schedules']):
				sc_data = json['schedules'][str(sc.hour).zfill(2) + str(sc.minute).zfill(2)]
				sc.status = ScheduleStatus(sc_data['status'])
		return day_obj

	def available(self):
		return any(s.status == ScheduleStatus.AVAILABLE for s in self.schedules)

	def assigned(self):
		return not self.available() and any(s.status == ScheduleStatus.ASSIGNED for s in self.schedules)

	def date_str(self):
		return str(self.day).zfill(2) + '/' + str(self.month).zfill(2) + '/' + str(self.year).zfill(4)
