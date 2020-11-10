from app import app, db
from flask import render_template, jsonify, send_from_directory, request
from config import Configuration
from cbr import CBR
import datetime
from models import Curs, Valuta
from sqlalchemy.exc import IntegrityError, InvalidRequestError


@app.route('/')
def index():

    return render_template('base.html')


@app.route('/load_data', methods=['GET'])
def load_data():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date is None or end_date is None:
        return render_template('load_data.html', state='new', error='')
    else:
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return render_template('load_data.html', state='false', error='Wrong dates')

        if start_date > end_date:
            return render_template('load_data.html', state='false', error='Start date is more than end date. Is wrong.')

        if end_date > datetime.datetime.now():
            return render_template('load_data.html', state='false', error='The end date is future! Is wrong.')

        days = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        print(days)
        cbr = CBR()
        for day in days:
            curs = cbr.get_curs_on_date(day.strftime('%Y-%m-%d'))
            for c in curs['curs']:
                if db.session.query(Valuta).get({'id': c['Vcode']}) is None:
                    valuta = Valuta(id=int(c['Vcode']), ch_code=c['VchCode'], name=c['Vname'])
                    db.session.add(valuta)
                    db.session.commit()

                if db.session.query(Curs).filter(Curs.code==c['Vcode']).filter(Curs.date==day.strftime('%Y-%m-%d')).first() is None:
                    curs_record = Curs(code=int(c['Vcode']), date=day, nom=c['Vnom'], curs=c['Vcurs'])
                    db.session.add(curs_record)
                    db.session.commit()

        return render_template('load_data.html', state='ok', error='')

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
