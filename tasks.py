import datetime
from models import Valuta, Curs
from cbr import CBR
from app import celery, db


app = celery


@app.task(trail=True)
def get_curs(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT00:00:00')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT00:00:00')

    days = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    cbr = CBR()
    for day in days:
        curs = cbr.get_curs_on_date(day.strftime('%Y-%m-%d'))
        for c in curs['curs']:
            if db.session.query(Valuta).get({'id': c['Vcode']}) is None:
                valuta = Valuta(id=int(c['Vcode']), ch_code=c['VchCode'], name=c['Vname'])
                db.session.add(valuta)
                db.session.commit()

            if db.session.query(Curs).filter(Curs.code == c['Vcode']).filter(
                    Curs.date == day.strftime('%Y-%m-%d')).first() is None:
                curs_record = Curs(code=int(c['Vcode']), date=day, nom=c['Vnom'], curs=c['Vcurs'])
                db.session.add(curs_record)
                db.session.commit()


