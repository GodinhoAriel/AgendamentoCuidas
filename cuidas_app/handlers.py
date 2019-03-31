from flask import render_template, flash, redirect, url_for, session
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
			day_objects=CalendarDay.get_calendar_month(year, month)))

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
			day_objects=CalendarDay.get_calendar_month(year, month)))
	
	@staticmethod
	def show_schedules(obj_response, year, month, day):
		obj_response.html('#schedules', render_template('schedule_table_agendamento.html', selected_day=CalendarDay.get_calendar_day(year, month, day)))

	@staticmethod
	def select_schedule(obj_response, year, month, day, hour, minute):
		day_obj = CalendarDay.get_calendar_day(year, month, day, True)
		schedule = next(s for s in day_obj.schedules if s.hour == hour and s.minute == minute)

		if(schedule.status == ScheduleStatus.AVAILABLE):
			schedule.name = session['name']
			schedule.email = session['email']
			schedule.phone = session['phone']
			schedule.status = ScheduleStatus.ASSIGNED

			day_obj.save()
			
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
			day_objects=CalendarDay.get_calendar_month(year, month)))

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
			day_objects=CalendarDay.get_calendar_month(year, month)))
	
	@staticmethod
	def show_schedules(obj_response, year, month, day):
		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=CalendarDay.get_calendar_day(year, month, day, True)))

	@staticmethod
	def enable_schedule(obj_response, year, month, day, hour, minute):
		day_obj = CalendarDay.get_calendar_day(year, month, day, True)
		schedule = next(s for s in day_obj.schedules if s.hour == hour and s.minute == minute)

		schedule.name = None
		schedule.email = None
		schedule.phone = None
		schedule.status = ScheduleStatus.AVAILABLE

		day_obj.save()

		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=day_obj))
		now = datetime.datetime.now()
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=CalendarDay.get_calendar_month(year, month)))

	@staticmethod
	def remove_schedule(obj_response, year, month, day, hour, minute):
		day_obj = CalendarDay.get_calendar_day(year, month, day, True)
		schedule = next(s for s in day_obj.schedules if s.hour == hour and s.minute == minute)

		schedule.name = None
		schedule.email = None
		schedule.phone = None
		schedule.status = ScheduleStatus.UNAVAILABLE

		day_obj.save()

		obj_response.html('#schedules', render_template('schedule_table_admin.html', selected_day=day_obj))
		now = datetime.datetime.now()
		obj_response.html('#calendar',
			render_template('calendar.html',
			calendar_inner=AdminCalendarHandler.calendar_inner,
			day_array=get_calendar(year, month),
			month_text=month_names[month-1],
			year=year,
			month=month,
			is_previous_month_available=not(year == now.year and month == now.month),
			day_objects=CalendarDay.get_calendar_month(year, month)))