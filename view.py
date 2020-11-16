from app import app, db
from flask import render_template, request, send_from_directory, abort
import datetime
from models import Curs, Valuta
from tasks import get_curs
from functions import check_tasks, convert_to_dict
from pandas import DataFrame, ExcelWriter
import os


@app.route('/')
def index():

    return render_template('base.html')


@app.route('/get_file/<file_type>/<valuta>/<start_date>/<end_date>')
def get_file(file_type, valuta, start_date, end_date):

    start_date_str = start_date
    end_date_str = end_date

    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d 00:00:00')
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d 00:00:00')

    curs = db.session.query(Curs).filter(Curs.date >= start_date,
                                         Curs.date <= end_date).filter(Curs.code == valuta).order_by(Curs.date).all()

    df = DataFrame(convert_to_dict(curs))
    df = df.drop(['_sa_instance_state', 'code', 'id'], axis=1)
    df = df[['date', 'nom', 'curs']]

    path_to_folder = os.getcwd() + '/tmp_file'

    filename = 'Curs_for_' + str(valuta) + '_' + start_date_str + '_' + end_date_str + '.' + file_type

    if file_type == 'csv':
        df.to_csv(path_to_folder + '/' + filename, index=False)
        return send_from_directory(directory=path_to_folder, filename=filename, as_attachment=True)
    elif file_type == 'xlsx':
        current_valuta = db.session.query(Valuta).filter(Valuta.id == valuta).one()
        writer = ExcelWriter(path_to_folder + '/' + filename, engine='xlsxwriter')
        df.to_excel(writer, index=False, startrow=3)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        worksheet.write(0, 0, 'Курс обмена валюты "' + current_valuta.name + '"')
        worksheet.write(1, 0, 'за период с ' + start_date_str + ' по ' + end_date_str)

        worksheet.set_column('A:A', 15)

        writer.save()
        return send_from_directory(directory=path_to_folder, filename=filename, as_attachment=True)
    else:
        return abort(404)


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

        get_curs.delay(start_date, end_date)

        return render_template('load_data.html', state='ok', error='', active_tasks=active_tasks)


@app.route('/show_data', methods=['GET'])
def show_data():
    valutes = db.session.query(Valuta).order_by(Valuta.name).all()

    start_date_str = request.args.get('start_date')

    if start_date_str in ['', None]:
        start_date_str = '1990-01-01'

    end_date_str = request.args.get('end_date')

    if end_date_str in ['', None]:
        end_date_str = datetime.datetime.now().strftime('%Y-%m-%d')

    valuta = request.args.get('valuta')

    if valuta in ['', None]:
        return render_template('show_data.html', valutes=valutes, state='ok', error='')

    current_valuta = db.session.query(Valuta).filter(Valuta.id==valuta).one()

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return render_template('show_data.html', state='false', error='Wrong dates')

    curs = db.session.query(Curs).filter(Curs.date>=start_date, Curs.date<=end_date).filter(Curs.code==valuta).order_by(Curs.date).all()

    return render_template('show_data.html',
                           valutes=valutes,
                           current_valuta=current_valuta,
                           curs=curs,
                           state='ok',
                           error='',
                           start_date=start_date,
                           end_date=end_date)
