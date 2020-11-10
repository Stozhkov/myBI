from app import db


class Curs(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    code = db.Column(db.Integer())
    date = db.Column(db.Date())
    nom = db.Column(db.Integer())
    curs = db.Column(db.Float())


class Valuta(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ch_code = db.Column(db.String(5))
    name = db.Column(db.String(200))
