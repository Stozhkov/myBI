from app import app, db
from flask import render_template, request
import datetime
from models import Curs, Valuta
from tasks import get_curs
from functions import check_tasks


@app.route('/')
def index():

    return render_template('base.html')


@app.route('/load_data', methods=['GET'])
def load_data():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    active_tasks = check_tasks()

    if start_date_str is None or end_date_str is None:
        return render_template('load_data.html', state='new', error='', active_tasks=active_tasks)
    else:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return render_template('load_data.html', state='false', error='Wrong dates')

        if start_date > end_date:
            return render_template('load_data.html', state='false', error='Start date is more than end date. Is wrong.')

        if end_date > datetime.datetime.now():
            return render_template('load_data.html', state='false', error='The end date is future! Is wrong.')

        # print(type(start_date))
        get_curs.delay(start_date, end_date)

        # task = Task(id=t.task_id, start_date=start_date_str, end_date=end_date_str)
        # db.session.add(task)
        # db.session.commit()

        # print(t.task_id)


        print(active_tasks)
        return render_template('load_data.html', state='ok', error='', active_tasks=active_tasks)


@app.route('/show_data', methods=['GET'])
def show_data():
    valutes = db.session.query(Valuta).order_by(Valuta.name).all()

    start_date = request.args.get('start_date')

    if start_date in ['', None]:
        start_date = '1990-01-01'

    end_date = request.args.get('end_date')

    if end_date in ['', None]:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    valuta = request.args.get('valuta')

    if valuta in ['', None]:
        return render_template('show_data.html', valutes=valutes, state='ok', error='')

    current_valuta = db.session.query(Valuta).filter(Valuta.id==valuta).one()
    print(current_valuta)

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return render_template('show_data.html', state='false', error='Wrong dates')

    curs = db.session.query(Curs).filter(Curs.date>=start_date, Curs.date<=end_date).filter(Curs.code==valuta).order_by(Curs.date).all()
    # print(curs)
    # print(valuta)

    return render_template('show_data.html', valutes=valutes, current_valuta=current_valuta, curs=curs, state='ok', error='')
