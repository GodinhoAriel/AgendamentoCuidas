from flask import render_template, flash, redirect, url_for, session
from cuidas_app import db
from cuidas_app.models import CalendarDay, ScheduleStatus
import datetime
import calendar

month_names = [
	'Janeiro',
	'Fevereiro',
	'Março',
	'Abril',
	'Maio',
	'Junho',
	'Julho',
	'Agosto',
	'Setembro',
	'Outubro',
	'Novembro',
	'Dezembro'
]

def get_calendar(year, month):
	calendar.setfirstweekday(calendar.SUNDAY)
	day_array = calendar.monthcalendar(year, month)
	return day_array

def get_day_objects(year, month):
	day_count = calendar.monthrange(year, month)[1]
	day_list = list(db.calendar_day.find({
			'year': year,
			'month': month
		}))
	day_objects = [CalendarDay.instantiate_from_json(day_json) for day_json in day_list]
	for day in range(1, day_count+1):
		if(not any(day_json['day'] == day for day_json in day_list)):
			day_objects.append(CalendarDay(year, month, day))

	day_objects.sort(key=lambda x: x.day)

	return day_objects
	
def get_day_objects_without_names(year, month):
	day_count = calendar.monthrange(year, month)[1]
	day_list = list(db.calendar_day.find({
			'year': year,
			'month': month
		}))
	day_objects = [CalendarDay.instantiate_from_json_without_names(day_json) for day_json in day_list]
	for day in range(1, day_count+1):
		if(not any(day_json['day'] == day for day_json in day_list)):
			day_objects.append(CalendarDay(year, month, day))

	day_objects.sort(key=lambda x: x.day)

	return day_objects

class CalendarHandler(object):
	calendar_inner = 'calendar_agendamento.html'

	@staticmethod
	def next(obj_response, year, month):
		now = datetime.datetime.now()
		month += 1
		if(month == 13):	
			year += 1
			month = 1
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=CalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects_without_names(year, month)))

	@staticmethod
	def previous(obj_response, year, month):
		now = datetime.datetime.now()
		month -= 1
		if(month == 0):	
			year -= 1
			month = 12
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=CalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects_without_names(year, month)))
	
	@staticmethod
	def show_schedules(obj_response, year, month, day):
		obj_response.html('#schedules', render_template('schedule_table_agendamento.html', selected_day=get_day_objects_without_names(year, month)[day-1]))

	@staticmethod
	def select_schedule(obj_response, year, month, day, hour, minute):
		day_obj = db.calendar_day.find_one({
			'year': year,
			'month': month,
			'day': day
		})
		if(day_obj['schedules'][str(hour).zfill(2) + str(minute).zfill(2)]['status'] == ScheduleStatus.AVAILABLE.value):
			day_obj['schedules'].update({
				str(hour).zfill(2) + str(minute).zfill(2): {
					'status': ScheduleStatus.ASSIGNED.value,
					'name': session['name'],
					'email': session['email'],
					'phone': session['phone']
				}
			})
			db.calendar_day.update({
				'year': year,
				'month': month,
				'day': day
			} , { '$set' : day_obj})
			flash('Agendamento cadastrado com sucesso!', 'success')
			session['schedule'] = str(day).zfill(2) + '/' + str(month).zfill(2) + '/' + str(year).zfill(4) + ' - ' + str(hour).zfill(2) + ':' + str(minute).zfill(2)
			obj_response.redirect(url_for('agendamento_sucesso'))
		else:
			flash('Horário indisponível, por favor tente outro horário.', 'danger')
			obj_response.redirect(url_for('agendamento_calendario'))

class AdminCalendarHandler(CalendarHandler):
	calendar_inner = 'calendar_admin.html'

	@staticmethod
	def next(obj_response, year, month):
		now = datetime.datetime.now()
		month += 1
		if(month == 13):	
			year += 1
			month = 1
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects(year, month)))

	@staticmethod
	def previous(obj_response, year, month):
		now = datetime.datetime.now()
		month -= 1
		if(month == 0):	
			year -= 1
			month = 12
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects(year, month)))
	
	@staticmethod
	def show_schedules(obj_response, year, month, day):
		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=get_day_objects(year, month)[day-1]))

	@staticmethod
	def enable_schedule(obj_response, year, month, day, hour, minute):
		day_obj = db.calendar_day.find_one({
			'year': year,
			'month': month,
			'day': day
		})
		if(not day_obj):
			day_obj = {
				'year': year,
				'month': month,
				'day': day,
				'schedules': {
					str(hour).zfill(2) + str(minute).zfill(2): {
						'status': ScheduleStatus.AVAILABLE.value,
						'name': None,
						'email': None,
						'phone': None
					}
				}
			}
		else:
			day_obj['schedules'].update({
				str(hour).zfill(2) + str(minute).zfill(2): {
					'status': ScheduleStatus.AVAILABLE.value,
					'name': None,
					'email': None,
					'phone': None
				}
			})
		db.calendar_day.update({
			'year': year,
			'month': month,
			'day': day
		} , { '$set' : day_obj} , True)
		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=CalendarDay.instantiate_from_json(day_obj)))
		now = datetime.datetime.now()
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects(year, month)))

	@staticmethod
	def remove_schedule(obj_response, year, month, day, hour, minute):
		day_obj = db.calendar_day.find_one({
			'year': year,
			'month': month,
			'day': day
		})
		day_obj['schedules'].update({
			str(hour).zfill(2) + str(minute).zfill(2): {
				'status': ScheduleStatus.UNAVAILABLE.value,
				'name': None,
				'email': None,
				'phone': None
			}
		})
		db.calendar_day.update({
			'year': year,
			'month': month,
			'day': day
		} , { '$set' : day_obj})
		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=CalendarDay.instantiate_from_json(day_obj)))
		now = datetime.datetime.now()
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=get_day_objects(year, month)))