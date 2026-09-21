import sqlite3
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
DB_NAME = "datos.db"

def get_db_connection():
    """Crea una conexión con la base de datos y permite acceder a columnas por nombre."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa las tablas en SQLite si no existen."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla para registros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala TEXT NOT NULL,
            texto TEXT NOT NULL,
            hora TEXT NOT NULL,
            asignacion TEXT DEFAULT ''
        )
    """)
    
    # Tabla para tareas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala TEXT NOT NULL,
            texto TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Inicializar las tablas al arrancar la aplicación
init_db()

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

# Vista principal de la sala: consulta los datos existentes en SQLite
@app.route('/<nombre_sala>')
def sala(nombre_sala):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    registros = cursor.execute(
        "SELECT * FROM registros WHERE sala = ? ORDER BY id ASC", 
        (nombre_sala,)
    ).fetchall()
    
    tareas = cursor.execute(
        "SELECT * FROM tareas WHERE sala = ? ORDER BY id ASC", 
        (nombre_sala,)
    ).fetchall()
    
    conn.close()
    return render_template('sala.html', nombre_sala=nombre_sala, registros=registros, tareas=tareas)

# ----------------- ENDPOINTS DE API (PERSISTENCIA CON SQLITE) -----------------

@app.route('/api/registros/agregar', methods=['POST'])
def api_agregar_registro():
    data = request.get_json() or {}
    sala = data.get('sala', '').strip()
    texto = data.get('texto', '').strip()
    
    if not sala or not texto:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    hora = datetime.now().strftime("%I:%M %p")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registros (sala, texto, hora, asignacion) VALUES (?, ?, ?, ?)",
        (sala, texto, hora, '')
    )
    nuevo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': nuevo_id, 'texto': texto, 'hora': hora, 'asignacion': ''})

@app.route('/api/registros/asignar', methods=['POST'])
def api_asignar_registro():
    data = request.get_json() or {}
    registro_id = data.get('registro_id')
    asignacion = data.get('asignacion', '').strip()
    
    if not registro_id or not asignacion:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # Concatena la nueva asignación si ya tenía alguna previa
    cursor.execute("SELECT asignacion FROM registros WHERE id = ?", (registro_id,))
    fila = cursor.fetchone()
    if not fila:
        conn.close()
        return jsonify({'success': False, 'error': 'Registro no encontrado'}), 404
        
    asignacion_actual = fila['asignacion']
    nueva_asignacion = f"{asignacion_actual} {asignacion}".strip()
    
    cursor.execute(
        "UPDATE registros SET asignacion = ? WHERE id = ?",
        (nueva_asignacion, registro_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'asignacion': nueva_asignacion})

@app.route('/api/tareas/agregar', methods=['POST'])
def api_agregar_tarea():
    data = request.get_json() or {}
    sala = data.get('sala', '').strip()
    texto = data.get('texto', '').strip()
    
    if not sala or not texto:
        return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tareas (sala, texto) VALUES (?, ?)",
        (sala, texto)
    )
    nuevo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': nuevo_id, 'texto': texto})

@app.route('/api/tareas/eliminar', methods=['POST'])
def api_eliminar_tarea():
    data = request.get_json() or {}
    tarea_id = data.get('tarea_id')
    
    if not tarea_id:
        return jsonify({'success': False, 'error': 'ID no proporcionado'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)