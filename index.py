import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# Credenciales de Supabase (puedes colocarlas directamente o en variables de entorno)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://atvybxjsolqmadzojkfm.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0dnlieGpzb2xxbWFkem9qa2ZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg4MDg3NTgsImV4cCI6MjEwNDM4NDc1OH0.ks66J_l5S8DQ9FHxpc4e0INNDzCRlUyDb-vnH_l4WvM")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/crear-sala', methods=['POST'])
def crear_sala():
    nombre = request.form.get('nombre_sala', '').strip()
    if nombre:
        return redirect(url_for('sala', nombre_sala=nombre))
    return redirect(url_for('home'))

# 1. CARGAR LA SALA: Solo consulta los datos que corresponden a esta sala
@app.route('/<nombre_sala>')
def sala(nombre_sala):
    # Consultar registros específicos de esta sala
    res_reg = supabase.table("registros").select("*").eq("sala", nombre_sala).order("id", desc=False).execute()
    registros = res_reg.data or []

    # Consultar tareas específicas de esta sala
    res_tar = supabase.table("tareas").select("*").eq("sala", nombre_sala).order("id", desc=False).execute()
    tareas = res_tar.data or []

    return render_template('sala.html', nombre_sala=nombre_sala, registros=registros, tareas=tareas)

# 2. AGREGAR REGISTRO: Lo guarda vinculado al nombre de la sala
@app.route('/api/registros/agregar', methods=['POST'])
def api_agregar_registro():
    data = request.get_json() or {}
    nombre_sala = data.get('sala', '').strip()
    texto = data.get('texto', '').strip()
    
    if not nombre_sala or not texto:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    hora = datetime.now().strftime("%I:%M %p")
    
    res = supabase.table("registros").insert({
        "sala": nombre_sala,
        "texto": texto,
        "hora": hora,
        "asignacion": ""
    }).execute()
    
    nuevo_registro = res.data[0]
    return jsonify({
        'success': True,
        'id': nuevo_registro['id'],
        'texto': nuevo_registro['texto'],
        'hora': nuevo_registro['hora'],
        'asignacion': ''
    })

# 3. ASIGNAR TAREA A UN REGISTRO
@app.route('/api/registros/asignar', methods=['POST'])
def api_asignar_registro():
    data = request.get_json() or {}
    registro_id = data.get('registro_id')
    asignacion = data.get('asignacion', '').strip()
    
    # Obtener el registro actual
    res = supabase.table("registros").select("asignacion").eq("id", registro_id).execute()
    if not res.data:
        return jsonify({'success': False, 'error': 'Registro no encontrado'}), 404
        
    asignacion_actual = res.data[0]['asignacion'] or ''
    nueva_asignacion = f"{asignacion_actual} {asignacion}".strip()
    
    supabase.table("registros").update({"asignacion": nueva_asignacion}).eq("id", registro_id).execute()
    return jsonify({'success': True, 'asignacion': nueva_asignacion})

# 4. ACTUALIZAR ASIGNACIÓN (para cuando borras con la 'x' roja)
@app.route('/api/registros/actualizar-asignacion', methods=['POST'])
def api_actualizar_asignacion():
    data = request.get_json() or {}
    registro_id = data.get('registro_id')
    nueva_asignacion = data.get('asignacion', '').strip()
    
    supabase.table("registros").update({"asignacion": nueva_asignacion}).eq("id", registro_id).execute()
    return jsonify({'success': True})

# 5. AGREGAR TAREA: Se guarda vinculada a la sala
@app.route('/api/tareas/agregar', methods=['POST'])
def api_agregar_tarea():
    data = request.get_json() or {}
    nombre_sala = data.get('sala', '').strip()
    texto = data.get('texto', '').strip()
    
    if not nombre_sala or not texto:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    res = supabase.table("tareas").insert({
        "sala": nombre_sala,
        "texto": texto
    }).execute()
    
    nueva_tarea = res.data[0]
    return jsonify({'success': True, 'id': nueva_tarea['id'], 'texto': nueva_tarea['texto']})

# 6. ELIMINAR TAREA
@app.route('/api/tareas/eliminar', methods=['POST'])
def api_eliminar_tarea():
    data = request.get_json() or {}
    tarea_id = data.get('tarea_id')
    
    supabase.table("tareas").delete().eq("id", tarea_id).execute()
    return jsonify({'success': True})

import urllib.parse

def obtener_fotos_carpeta(carpeta):
    ruta = carpeta.strip("/")
    urls = []
    try:
        archivos = supabase.storage.from_("fotos").list(ruta)
        print(f"\n[STORAGE] Listando carpeta: '{ruta}'")
        print(f"[STORAGE] Archivos encontrados: {archivos}")
        
        for arch in archivos:
            nombre = arch.get("name", "")
            # Descartar archivos vacíos o de sistema
            if nombre and not nombre.startswith("."):
                url = supabase.storage.from_("fotos").get_public_url(f"{ruta}/{nombre}")
                urls.append(url)
                
        print(f"[STORAGE] URLs generadas para '{ruta}': {len(urls)}")
    except Exception as e:
        print(f"[STORAGE ERROR] En carpeta '{ruta}': {e}")
    return urls


@app.route('/proyectos')
def proyectos():
    # Tu número de WhatsApp (+51 para Perú)
    numero_whatsapp = "51975177733"

    # Mensajes personalizados pre-armados para cada botón
    msg_web = urllib.parse.quote("Hola, me interesa conocer más sobre sus Aplicativos web y móviles.")
    msg_exe = urllib.parse.quote("Hola, quisiera información sobre las Interfaces y Software Ejecutables.")
    msg_num = urllib.parse.quote("Hola, me gustaría consultar sobre los programas de Métodos Numéricos.")

    # Cargar URLs directamente desde las carpetas del bucket
    fotos_web = obtener_fotos_carpeta("web_movil")
    fotos_exe = obtener_fotos_carpeta("ejecutables")
    fotos_met = obtener_fotos_carpeta("metodos")

    return render_template(
        'proyectos.html',
        fotos_web=fotos_web,
        fotos_exe=fotos_exe,
        fotos_met=fotos_met,
        tk_link=f"https://www.tiktok.com/@mtodos.numricos",
        wa_web=f"https://wa.me/{numero_whatsapp}?text={msg_web}",
        wa_exe=f"https://wa.me/{numero_whatsapp}?text={msg_exe}",
        wa_num=f"https://wa.me/{numero_whatsapp}?text={msg_num}"
    )

if __name__ == '__main__':
    app.run(debug=True)