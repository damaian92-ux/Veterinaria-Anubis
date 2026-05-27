from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Dueño(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.String(200))
    mascotas = db.relationship('Mascota', backref='dueño', lazy=True)

class Mascota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50))
    raza = db.Column(db.String(50))
    edad = db.Column(db.Integer)
    dueño_id = db.Column(db.Integer, db.ForeignKey('dueño.id'), nullable=False)

    historias = db.relationship('HistoriaClinica', backref='mascota', lazy=True)
    vacunas = db.relationship('Vacuna', backref='mascota', lazy=True)
    desparasitaciones = db.relationship('Desparasitacion', backref='mascota', lazy=True)
    cirugias = db.relationship('Cirugia', backref='mascota', lazy=True)

from datetime import date

class HistoriaClinica(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fecha = db.Column(db.Date, default=date.today)

    diagnostico = db.Column(db.Text)

    tratamiento = db.Column(db.Text)
    
    evoluciones = db.relationship('EvolucionClinica',backref='historia',lazy=True)

    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'))

class EvolucionClinica(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    historia_id = db.Column(
        db.Integer,
        db.ForeignKey('historia_clinica.id'),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    descripcion = db.Column(db.Text, nullable=False)

class Vacuna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    proxima_dosis = db.Column(db.Date)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)

class Desparasitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    proxima_aplicacion = db.Column(db.Date)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)

class Cirugia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)
    
class Tratamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date)
    proxima = db.Column(db.Date)
    observaciones = db.Column(db.Text)

    mascota_id = db.Column(db.Integer, db.ForeignKey('mascota.id'), nullable=False)
    mascota = db.relationship('Mascota', backref='tratamientos')    