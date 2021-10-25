from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField
from . models import Admins, Respuestas, Usuarios, Preguntas, Areas, Subgrupos, Opciones, SubgruposForm, AreasForm
from io import BytesIO
from . import db
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

views = Blueprint("views", __name__)

@views.route("/", methods=['GET', 'POST'])
@views.route("/index", methods=['GET', 'POST'])
def iniciarTest():
    if request.method == 'POST':

        name = request.form.get("name")

        name_exists = Usuarios.query.filter_by(name=name).first()

        if name_exists:
            flash('Usuario ya esta en uso.', category='error')

        elif len(name) < 2:
            flash('El usuario tiene que tener mas de 2 caracteres.', category='error')

        else:
            new_user = Usuarios(name=name)
            
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario creado.', category='success')
            usuario = Usuarios.query.filter_by(name=name).first()
            areas = Areas.query.order_by(Areas.orden).first()
            return redirect(url_for('views.test', usuario=usuario.id, id=areas.id))

    return render_template("index.html", user=current_user)


@views.route("/preguntas", methods=['GET', 'POST'])
@login_required
def preguntas():
    areas = AreasForm()
    if request.method == 'POST':

        pregunta_descripcion = request.form.get("pregunta_descripcion")
        tipo_checkbox = request.form.get("tipo")
        puntaje = request.form.get("puntaje")

        areas.opts.query = Areas.query.filter(Areas.id > 1)

        if areas.opts.data == None:
            area = 1
        else:
            area = areas.opts.data.id

        if tipo_checkbox == None:
            tipo=False
        else:
            tipo=True

        nueva_pregunta = Preguntas(pregunta_descripcion=pregunta_descripcion,tipo=tipo,puntaje=puntaje,area=area)
        
        db.session.add(nueva_pregunta)
        db.session.commit()
        flash('Pregunta Creada.', category='success')
    
    preguntas = Preguntas.query.all()

    return render_template("preguntas.html", preguntas=preguntas, areas=areas, user=current_user)

@views.route("/delete-pregunta/<id>")
@login_required
def eliminar_pregunta(id):
    pregunta = Preguntas.query.filter_by(id=id).first()

    if not pregunta:
        flash("La pregunta no existe.", category='error')
    
    else:
        db.session.delete(pregunta)
        db.session.commit()
        flash("Se ha eliminado la pregunta satisfactoriamente.", category='success')

    return redirect(url_for('views.preguntas'))

@views.route("/editar_pregunta/<id>")
@login_required
def editar_pregunta(id):

    pregunta = Preguntas.query.filter_by(id=id).first()

    return render_template("editar_pregunta.html", pregunta=pregunta, user=current_user)

@views.route("/update/<id>", methods=['POST'])
@login_required
def update_pregunta(id):
    if request.method == 'POST':

        pregunta_descripcion = request.form.get("pregunta_descripcion")
        tipo_checkbox = request.form.get("tipo")
        puntaje = request.form.get("puntaje")
        if tipo_checkbox == None:
            tipo=False
        else:
            tipo=True

        pregunta = Preguntas.query.filter_by(id=id).update(dict(pregunta_descripcion=pregunta_descripcion,tipo=tipo,puntaje=puntaje))
        db.session.commit()
        flash('Pregunta editada correctamente.', category='success')

    return redirect(url_for('views.preguntas'))

@views.route("/subgrupos", methods=['GET', 'POST'])
@login_required
def subgrupos():
    if request.method == 'POST':

        nombre_subgrupo = request.form.get("nombre_subgrupo")
        nuevo_subgrupo = Subgrupos(nombre_subgrupo=nombre_subgrupo)
        
        db.session.add(nuevo_subgrupo)
        db.session.commit()
        flash('SubGrupo Creado.', category='success')
    
    subgrupos = Subgrupos.query.all()

    return render_template("subgrupos.html", subgrupos=subgrupos, user=current_user)

@views.route("/delete-subgrupo/<id>")
@login_required
def eliminar_subgrupo(id):
    subgrupo = Subgrupos.query.filter_by(id=id).first()

    if not subgrupo:
        flash("El Subgrupo no existe.", category='error')
    
    else:
        db.session.delete(subgrupo)
        db.session.commit()
        flash("Se ha eliminado el subgrupo satisfactoriamente.", category='success')

    return redirect(url_for('views.subgrupos'))

@views.route('/areas', methods=['GET', 'POST'])
@login_required
def areas():
    subgrupos = SubgruposForm()

    if request.method == 'POST':

        nombre_area = request.form.get("nombre_area")
        orden = request.form.get("orden")

        orden_exists = Areas.query.filter_by(orden=orden).first()
        

        subgrupos.opts.query = Subgrupos.query.filter(Subgrupos.id > 1)

        if subgrupos.opts.data == None:
            sub_grupo = 1
        else:
            sub_grupo = subgrupos.opts.data.id

        if nombre_area=="":
            flash("El area no puede estar vacia.", category='error')

        elif sub_grupo == None:
            flash("Seleccione un subgrupo valido", category='error')
        
        elif orden_exists:
            flash('El orden ya esta en uso.', category='error')
        
        else:
            nuevo_area = Areas(nombre_area=nombre_area,sub_grupo=sub_grupo,orden=orden)
            db.session.add(nuevo_area)
            db.session.commit()

    areas = Areas.query.order_by(Areas.orden)

    return render_template('areas.html', subgrupos=subgrupos, areas=areas, user=current_user)

@views.route("/editar_area/<id>")
@login_required
def editar_area(id):

    area = Areas.query.filter_by(id=id).first()
    subgrupos = SubgruposForm()

    return render_template("editar_area.html", subgrupos=subgrupos, area=area, user=current_user)

@views.route("/update_area/<id>", methods=['POST'])
@login_required
def update_area(id):
    if request.method == 'POST':
        
        subgrupos = SubgruposForm()

        nombre_area = request.form.get("nombre_area")
        orden = request.form.get("orden")

        orden_exists = Areas.query.filter_by(orden=orden).first()
        

        subgrupos.opts.query = Subgrupos.query.filter(Subgrupos.id > 1)

        if orden_exists:
            flash('El orden ya esta en uso.', category='error')

        elif subgrupos.validate_on_submit():
            sub_grupo = subgrupos.opts.data

            area = Areas.query.filter_by(id=id).update(dict(nombre_area=nombre_area,sub_grupo=sub_grupo.id,orden=orden))
            db.session.commit()
            flash('Area editada correctamente.', category='success')

    return redirect(url_for('views.areas'))

@views.route("/delete-area/<id>")
@login_required
def eliminar_area(id):
    area = Areas.query.filter_by(id=id).first()

    if not area:
        flash("El Area no existe.", category='error')
    
    else:
        db.session.delete(area)
        db.session.commit()
        flash("Se ha eliminado el area satisfactoriamente.", category='success')

    return redirect(url_for('views.areas'))

@views.route('/opciones/<id>', methods=['GET', 'POST'])
@login_required
def opciones(id):
    if request.method == 'POST':

        pregunta = id
        opcion = request.form.get("opcion")
        tipo_correcta = request.form.get("correcta")
        orden = request.form.get("orden")

        orden_exists = Opciones.query.filter_by(orden=orden, pregunta=pregunta).first()

        if tipo_correcta == None:
            correcta=False
        else:
            correcta=True

        if orden_exists:
            flash('El orden ya esta en uso.', category='error')
        else:
            nuevo_opcion = Opciones(opcion=opcion,correcta=correcta,orden=orden,pregunta=pregunta)
            db.session.add(nuevo_opcion)
            db.session.commit()


    opciones = Opciones.query.filter_by(pregunta=id).order_by(Opciones.orden)
    preguntas = Preguntas.query.filter_by(id=id).first()

    return render_template('opciones.html', opciones=opciones, preguntas=preguntas, user=current_user)

@views.route("/delete-opcion/<id>")
@login_required
def eliminar_opcion(id):
    opcion = Opciones.query.filter_by(id=id).first()

    if not opcion:
        flash("La Opcion no existe.", category='error')
    
    else:
        db.session.delete(opcion)
        db.session.commit()
        flash("Se ha eliminado la opcion satisfactoriamente.", category='success')

    return redirect(url_for('views.opciones', id=opcion.pregunta))

@views.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        user = Admins.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                flash('Ha iniciado sesion correctamente.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.login'))
            else:
                flash('La contraseña es incorrecta.', category='error')
        else:
            flash('El usuario no existe o es incorrecto.', category='error')

    return render_template('login.html', user=current_user)

@views.route("/crearadmin", methods=['GET', 'POST'])
def crear_admin():

    admin = Admins(username='admin',password='0')
    db.session.add(admin)
    db.session.commit()

    return redirect(url_for('views.login'))


@views.route("/test/<usuario>/<id>", methods=['GET', 'POST'])
def test(usuario,id):
    preguntas = Preguntas.query.all()
    opciones = Opciones.query.order_by(Opciones.orden)
    areas = Areas.query.filter_by(orden=id).first()
    max_area = Areas.query.order_by(Areas.orden.desc()).first()
    usuario = Usuarios.query.filter_by(id=usuario).first()

    if request.method == 'POST':
        respuestas = request.form.getlist('respuesta')
        
        print(respuestas)

        if areas.orden == max_area.orden:
            for respuesta in respuestas:
                add_respuesta = Respuestas(usuario=usuario.id,respuesta=respuesta)
                db.session.add(add_respuesta)
                db.session.commit()
            return redirect(url_for('views.resultados'))
        else:
            siguiente = int(id) + 1
            for respuesta in respuestas:
                add_respuesta = Respuestas(usuario=usuario.id,respuesta=respuesta)
                db.session.add(add_respuesta)
                db.session.commit()
            return redirect(url_for('views.test', usuario=usuario.id, id=siguiente))


    return render_template("test.html", preguntas=preguntas, opciones=opciones, user=current_user, areas=areas, max_area=max_area, usuario=usuario)

@views.route("/resultados", methods=['GET', 'POST'])
def resultados():

    return render_template("resultados.html", user=current_user)
