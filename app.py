import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

template_dir = os.path.join(base_path, "templates")
static_dir = os.path.join(base_path, "static")

from flask import Flask, render_template, request, redirect, url_for, send_file
from models import db, Dueño, Mascota, HistoriaClinica, Tratamiento, EvolucionClinica
from datetime import datetime
import os
from reportlab.pdfgen import canvas
import webbrowser

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
else:
    template_folder = 'templates'
    static_folder = 'static'

app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

db_path = os.path.join(base_path, "instance", "veterinaria.db")

import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
   import os

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///veterinaria.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- INICIO ----------------

@app.route('/')
def index():
    return render_template("index.html")


# ---------------- DUEÑOS ----------------

@app.route('/dueños', methods=['GET','POST'])
def dueños():

    if request.method == 'POST':

        nuevo = Dueño(
            nombre=request.form['nombre'],
            telefono=request.form['telefono'],
            direccion=request.form['direccion']
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for('dueños'))

    lista = Dueño.query.all()

    return render_template("dueños.html", dueños=lista)


# ---------------- MASCOTAS ----------------

@app.route('/mascotas', methods=['GET','POST'])
def mascotas():

    dueños = Dueño.query.all()

    if request.method == 'POST':

        edad = request.form.get('edad') or None

        nueva = Mascota(
            nombre=request.form['nombre'],
            especie=request.form['especie'],
            raza=request.form['raza'],
            edad=edad,
            dueño_id=request.form['dueño_id']
        )

        db.session.add(nueva)
        db.session.commit()

        return redirect(url_for('mascotas'))

    mascotas = Mascota.query.all()

    return render_template("mascotas.html", mascotas=mascotas, dueños=dueños)


# ---------------- HISTORIA CLINICA ----------------

@app.route("/historia", methods=["GET", "POST"])
def historia():

    mascotas = Mascota.query.all()

    if request.method == "POST":

        mascota_id = request.form["mascota_id"]
        diagnostico = request.form["diagnostico"]
        tratamiento = request.form["tratamiento"]

        nueva = HistoriaClinica(
            mascota_id=mascota_id,
            diagnostico=diagnostico,
            tratamiento=tratamiento
        )

        db.session.add(nueva)
        db.session.commit()

        return redirect("/historias")

    # -------------------------
    # GENERAR DATOS PARA HTML
    # -------------------------

    ultimo = HistoriaClinica.query.order_by(HistoriaClinica.id.desc()).first()
    hc_numero = f"HC-{(ultimo.id + 1) if ultimo else 1:05d}"

    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    mascotas_json = [
        {
            "id": m.id,
            "nombre": m.nombre,
            "raza": m.raza,
            "especie": m.especie,
            "dueño": m.dueño.nombre if m.dueño else "",
            "telefono": m.dueño.telefono if m.dueño else "",
            "direccion": m.dueño.direccion if m.dueño else ""
        }
        for m in mascotas
    ]

    return render_template(
        "historia.html",
        mascotas=mascotas,
        hc_numero=hc_numero,
        fecha_hora=fecha_hora,
        mascotas_json=mascotas_json
    )


# ---------------- VER HISTORIAS ----------------

@app.route('/historias')
def ver_historias():

    historias = HistoriaClinica.query.all()

    return render_template(
        "ver_historias.html",
        historias=historias
    )

# ---------------- GENERAR PDF ----------------

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle


@app.route('/pdf/<int:id>')
def generar_pdf(id):

    historia = HistoriaClinica.query.get_or_404(id)

    mascota = Mascota.query.get(historia.mascota_id)

    dueño = Dueño.query.get(mascota.dueño_id)

    ruta_pdf = f"historia_{id}.pdf"

    c = canvas.Canvas(ruta_pdf, pagesize=letter)

    width, height = letter

    styles = getSampleStyleSheet()

    # =====================================================
    # VARIABLES
    # =====================================================

    y = height - 50

    color_principal = colors.HexColor("#1f3c88")

    color_secundario = colors.HexColor("#e8eefc")

    # =====================================================
    # FUNCIONES
    # =====================================================

    def nueva_pagina():

        nonlocal y

        c.showPage()

        y = height - 50

    def verificar_espacio(espacio=120):

        nonlocal y

        if y < espacio:
            nueva_pagina()

    def titulo(texto):

        nonlocal y

        verificar_espacio(80)

        c.setFillColor(color_principal)

        c.roundRect(35, y - 8, width - 70, 25, 8, fill=1, stroke=0)

        c.setFillColor(colors.white)

        c.setFont("Helvetica-Bold", 13)

        c.drawString(50, y, texto.upper())

        y -= 35

    def campo(label, valor):

        nonlocal y

        verificar_espacio(40)

        c.setFillColor(colors.black)

        c.setFont("Helvetica-Bold", 11)

        c.drawString(50, y, f"{label}:")

        c.setFont("Helvetica", 11)

        texto = str(valor) if valor else "-"

        c.drawString(170, y, texto)

        y -= 20

    def caja_texto(label, texto):

        nonlocal y

        verificar_espacio(160)

        c.setFont("Helvetica-Bold", 12)

        c.setFillColor(color_principal)

        c.drawString(50, y, label)

        y -= 18

        alto = 90

        c.setFillColor(color_secundario)

        c.roundRect(45, y - alto + 10, width - 90, alto, 10, fill=1, stroke=0)

        c.setFillColor(colors.black)

        estilo = ParagraphStyle(
            'normal',
            fontName='Helvetica',
            fontSize=10,
            leading=16
        )

        p = Paragraph(str(texto or "-"), estilo)

        frame = Frame(
            60,
            y - alto + 20,
            width - 120,
            alto - 20,
            showBoundary=0
        )

        frame.addFromList([p], c)

        y -= alto + 20

    # =====================================================
    # LOGO
    # =====================================================

    logo_path = os.path.join(base_path, "static", "logo.png")

    if os.path.exists(logo_path):

        c.drawImage(
            logo_path,
            40,
            height - 110,
            width=70,
            height=70,
            mask='auto'
        )

        # Marca de agua

        c.saveState()

        c.setFillAlpha(0.05)

        c.drawImage(
            logo_path,
            width / 2 - 170,
            height / 2 - 170,
            width=340,
            height=340,
            mask='auto'
        )

        c.restoreState()

    # =====================================================
    # ENCABEZADO
    # =====================================================

    c.setFillColor(color_principal)

    c.setFont("Helvetica-Bold", 24)

    c.drawString(130, height - 60, "Veterinaria Anubis")

    c.setFont("Helvetica", 13)

    c.drawString(130, height - 85, "Historia Clínica Veterinaria")

    c.setStrokeColor(color_principal)

    c.setLineWidth(2)

    c.line(40, height - 120, width - 40, height - 120)

    y = height - 155

    # =====================================================
    # DATOS GENERALES
    # =====================================================

    titulo("Datos Generales")

    campo("HC N°", getattr(historia, 'hc_numero', ''))

    campo(
        "Fecha",
        getattr(historia, 'fecha_hora', historia.fecha)
    )

    campo("Propietario", dueño.nombre)

    campo("Teléfono", dueño.telefono)

    campo("Dirección", dueño.direccion)

    # =====================================================
    # PACIENTE
    # =====================================================

    titulo("Datos del Paciente")

    campo("Paciente", mascota.nombre)

    campo("Especie", mascota.especie)

    campo("Raza", mascota.raza)

    campo("Sexo", getattr(historia, 'sexo', ''))

    campo("Peso", f"{getattr(historia, 'peso', '')} kg")

    campo(
        "Color / Pelaje",
        getattr(historia, 'color_pelaje', '')
    )

    campo(
        "Identificación Particular",
        getattr(historia, 'identificacion_particular', '')
    )

    campo(
        "Esterilizado",
        getattr(historia, 'esterilizado', '')
    )

    # =====================================================
    # SECCIONES CLINICAS
    # =====================================================

    caja_texto(
        "Dieta",
        getattr(historia, 'dieta', '')
    )

    caja_texto(
        "Enfermedades Previas",
        getattr(historia, 'enfermedades_previas', '')
    )

    caja_texto(
        "Motivo de Consulta",
        getattr(historia, 'motivo', '')
    )

    caja_texto(
        "Diagnóstico",
        historia.diagnostico
    )

    caja_texto(
        "Tratamiento Indicado",
        historia.tratamiento
    )

    # =====================================================
    # EVOLUCIONES CLINICAS
    # =====================================================

    if historia.evoluciones:

        titulo("Evoluciones Clínicas")

        for evo in historia.evoluciones:

            verificar_espacio(140)

            fecha = evo.fecha.strftime("%d/%m/%Y %H:%M")

            c.setFillColor(color_principal)

            c.roundRect(45, y - 5, width - 90, 22, 6, fill=1, stroke=0)

            c.setFillColor(colors.white)

            c.setFont("Helvetica-Bold", 10)

            c.drawString(55, y + 2, fecha)

            y -= 30

            alto = 70

            c.setFillColor(colors.whitesmoke)

            c.roundRect(
                45,
                y - alto + 10,
                width - 90,
                alto,
                8,
                fill=1,
                stroke=0
            )

            c.setFillColor(colors.black)

            estilo = ParagraphStyle(
                'evolucion',
                fontName='Helvetica',
                fontSize=10,
                leading=15
            )

            p = Paragraph(evo.descripcion, estilo)

            frame = Frame(
                60,
                y - alto + 20,
                width - 120,
                alto - 20,
                showBoundary=0
            )

            frame.addFromList([p], c)

            y -= alto + 20

    # =====================================================
    # FIRMA
    # =====================================================

    verificar_espacio(120)

    y -= 30

    c.setStrokeColor(colors.black)

    c.line(350, y, 550, y)

    y -= 20

    c.setFont("Helvetica", 10)

    c.drawString(405, y, "Firma Veterinario")

    # =====================================================
    # PIE DE PAGINA
    # =====================================================

    c.setFont("Helvetica", 9)

    c.setFillColor(colors.grey)

    c.drawCentredString(
        width / 2,
        20,
        "Veterinaria Anubis - Sistema de Gestión Veterinaria"
    )

    # =====================================================
    # GUARDAR
    # =====================================================

    c.save()

    return send_file(ruta_pdf, as_attachment=True)


@app.route('/ampliar_historia/<int:id>', methods=['GET', 'POST'])
def ampliar_historia(id):

    historia = HistoriaClinica.query.get_or_404(id)

    if request.method == 'POST':

        descripcion = request.form['descripcion']

        nueva = EvolucionClinica(
            historia_id=id,
            descripcion=descripcion
        )

        db.session.add(nueva)
        db.session.commit()

        return redirect(url_for('historial_mascota', mascota_id=historia.mascota_id))

    return render_template(
        'ampliar_historia.html',
        historia=historia
    )


# ---------------- TRATAMIENTOS ----------------

from datetime import datetime

@app.route('/tratamiento', methods=['GET', 'POST'])
def tratamiento():

    mascotas = Mascota.query.all()

    if request.method == 'POST':

        tipo = request.form['tipo']
        nombre = request.form['nombre']
        mascota_id = request.form['mascota_id']
        observaciones = request.form['observaciones']

        # FECHA OBLIGATORIA
        fecha = datetime.strptime(request.form['fecha'], "%Y-%m-%d").date()

        # PROXIMA OPCIONAL
        proxima = request.form.get('proxima')

        if proxima:
            proxima = datetime.strptime(proxima, "%Y-%m-%d").date()
        else:
            proxima = None

        nuevo = Tratamiento(
            tipo=tipo,
            nombre=nombre,
            fecha=fecha,
            proxima=proxima,
            observaciones=observaciones,
            mascota_id=mascota_id
        )

        db.session.add(nuevo)
        db.session.commit()

        return redirect(url_for('ver_tratamientos'))

    return render_template('tratamiento.html', mascotas=mascotas)

@app.route("/ver_tratamientos")
def ver_tratamientos():

    tratamientos = Tratamiento.query.all()

    datos = []

    from datetime import date

    for t in tratamientos:

        mascota = db.session.get(Mascota, t.mascota_id)

        color = "verde"

        if t.proxima:

            hoy = date.today()
            dias = (t.proxima - hoy).days

            if dias <= 0:
                color = "roja"
            elif dias <= 30:
                color = "amarilla"

        datos.append([
            mascota.nombre,
            t.tipo,
            t.nombre,
            t.fecha,
            t.proxima,
            t.observaciones,
            color
        ])

    return render_template("ver_tratamientos.html", datos=datos)

@app.route("/historial/<int:mascota_id>")
def historial_mascota(mascota_id):

    mascota = db.session.get(Mascota, mascota_id)

    dueño = db.session.get(Dueño, mascota.dueño_id)

    historias = HistoriaClinica.query.filter_by(mascota_id=mascota_id).all()

    tratamientos = Tratamiento.query.filter_by(mascota_id=mascota_id).all()

    return render_template(
        "historial_mascota.html",
        mascota=mascota,
        dueño=dueño,
        historias=historias,
        tratamientos=tratamientos
    )


# ---------------- RUN ----------------

import threading
import time

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)