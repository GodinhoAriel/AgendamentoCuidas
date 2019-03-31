from flask import render_template, url_for, flash, redirect, session
from flask_login import login_user, current_user, logout_user, login_required
from cuidas_app import app, bcrypt, flask_sijax, g
from cuidas_app.forms import LoginForm, AgendamentoForm
from cuidas_app.models import User, CalendarDay, Schedule, ScheduleStatus
from cuidas_app.handlers import CalendarHandler, AdminCalendarHandler, get_calendar, month_names
import datetime


@app.route("/", methods=['GET', 'POST'])
@app.route("/agendamento", methods=['GET', 'POST'])
def agendamento():
	form = AgendamentoForm()

	if form.validate_on_submit():
		session['name'] = form.name.data
		session['email'] = form.email.data
		session['phone'] = form.phone.data
		return redirect(url_for('agendamento_calendario'))
	return render_template('agendamento.html', title='Agendamento',	form=form)

@flask_sijax.route(app, "/agendamento/calendario")
def agendamento_calendario():
	if g.sijax.is_sijax_request:
		g.sijax.register_object(CalendarHandler)
		return g.sijax.process_request()

	now = datetime.datetime.now()
	year = now.year
	month = now.month
	return render_template('agendamento_calendar.html',
		title='Agendamento',
		name=session['name'],
		email=session['email'],
		phone=session['phone'],
		calendar_inner='calendar_agendamento.html',
		day_array=get_calendar(year, month),
		month_text=month_names[month-1],
		year=year,
		month=month,
		is_previous_month_available=not(year == now.year and month == now.month),
		day_objects=CalendarDay.get_calendar_month(year, month))


@flask_sijax.route(app, "/agendamento/sucesso")
def agendamento_sucesso():
	return render_template('agendamento_success.html',
		title='Agendamento',
		name=session['name'],
		email=session['email'],
		phone=session['phone'],
		schedule=session['schedule'])
	
@flask_sijax.route(app, "/admin")
@login_required
def admin():	
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	if g.sijax.is_sijax_request:
		g.sijax.register_object(AdminCalendarHandler)
		return g.sijax.process_request()

	now = datetime.datetime.now()
	year = now.year
	month = now.month
	return render_template('admin.html', 
		title='Admin',
		calendar_inner='calendar_admin.html',
		day_array=get_calendar(year, month),
		month_text=month_names[month-1],
		year=year,
		month=month,
		is_previous_month_available=not(year == now.year and month == now.month),
		day_objects=CalendarDay.get_calendar_month(year, month))

@app.route("/admin/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('admin'))
	
	form = LoginForm()
	if form.validate_on_submit():
		user = User.get_by_email(form.email.data)
		# Checar se o usuário existe e seo hash é compatível com a senha
		if user and bcrypt.check_password_hash(user.hash, form.password.data):
			result = login_user(user, remember=form.remember.data)
			flash('Você se autenticou com sucesso!', 'success')
			return redirect(url_for('admin'))
		else:
			flash('A autenticação falhou. Por favor verifique seu email e senha.', 'danger')

	return render_template('login.html', title='Login', form=form)

@app.route("/admin/logout")
def logout():
	logout_user()
	return redirect(url_for('login'))