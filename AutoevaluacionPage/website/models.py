from enum import unique
from flask import config
from sqlalchemy.orm import backref
from sqlalchemy.sql.expression import false, text
from . import db
from sqlalchemy.sql import func
from . import app
from flask_wtf import FlaskForm 
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import UserMixin

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())
    respuesta = db.relationship('Respuestas', backref='res', passive_deletes=True)

class Admins(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date_create = db.Column(db.DateTime(timezone=True), default=func.now())

class Preguntas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pregunta_descripcion = db.Column(db.String)
    opciones = db.relationship('Opciones', backref='preg', passive_deletes=True)
    puntaje = db.Column(db.Float)
    tipo = db.Column(db.Boolean)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())
    area = db.Column(db.Integer, db.ForeignKey('areas.id', ondelete="CASCADE"), nullable=False)

class Opciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opcion = db.Column(db.String, nullable=False)
    correcta = db.Column(db.Boolean)
    orden = db.Column(db.Integer)
    pregunta = db.Column(db.Integer, db.ForeignKey('preguntas.id', ondelete="CASCADE"), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())
    respuesta = db.relationship('Respuestas', backref='respreg', passive_deletes=True)

class Areas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_area = db.Column(db.String)
    sub_grupo = db.Column(db.Integer, db.ForeignKey('subgrupos.id', ondelete="CASCADE"), nullable=False)
    orden = db.Column(db.Integer)
    pregunta = db.relationship('Preguntas', backref='areas', passive_deletes=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())

class Subgrupos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_subgrupo = db.Column(db.String)
    area = db.relationship('Areas', backref='subgrupos', passive_deletes=True)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())

class Respuestas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    respuesta = db.Column(db.Integer, db.ForeignKey('opciones.id', ondelete="CASCADE"), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=func.now())

def subgrupos_query():
    return Subgrupos.query

class SubgruposForm(FlaskForm):
    opts = QuerySelectField(query_factory=subgrupos_query, allow_blank=False, get_label='nombre_subgrupo')

def areas_query():
    return Areas.query

class AreasForm(FlaskForm):
    opts = QuerySelectField(query_factory=areas_query, allow_blank=False, get_label='nombre_area')