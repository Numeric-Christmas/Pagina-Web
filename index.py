import matplotlib
# ¡VITAL! Cambia el motor gráfico a 'Agg' para que funcione en servidores web sin pantalla
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from flask import Flask, render_template

app = Flask(__name__)

def generar_corazon_html():
    NUM_FILAS = 32
    NUM_COLUMNAS = 40
    TITULO = "Hecho con <3, MÉTODOS NUMÉRICOS"
    MENSAJE_ANIMADO = "MÉTODOS NUMÉRICOS"

    def inside_heart(x, y):
        x_scaled = x * 1.5
        y_scaled = (y - 0.2) * 1.5 
        return (x_scaled**2 + (y_scaled - np.sqrt(np.abs(x_scaled)))**2) <= 1.0

    x_vals = np.linspace(-1.3, 1.3, NUM_COLUMNAS)
    y_vals_1d = np.linspace(-1.1, 1.4, NUM_FILAS)[::-1] 

    y_filas = []
    for y in y_vals_1d:
        fila = [(xi, y) for xi in x_vals]
        y_filas.append(fila)

    fig, ax = plt.subplots(figsize=(8, 7))
    fig.set_facecolor('#0d1117') 
    ax.set_facecolor('#0d1117')
    ax.axis('off') 
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.3, 1.6)

    for fila_puntos in y_filas:
        for xi, yi in fila_puntos:
            if inside_heart(xi, yi):
                ax.text(xi, yi, '❤️', color='#ff1744', fontsize=11, alpha=1, 
                        ha='center', va='center', fontname='sans-serif')

    plt.title(TITULO, fontsize=14, color='white', fontname='sans-serif', pad=20)

    anim_text = ax.text(0, 0, MENSAJE_ANIMADO, fontsize=13, color='#00ffff', 
                        fontweight='bold', ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#0d1117', edgecolor='none', alpha=0.9),
                        zorder=10, visible=False)

    def update_frame(k):
        if k < len(y_filas):
            y_pos = y_filas[k][0][1]
            anim_text.set_position((0, y_pos))
            anim_text.set_visible(True)
            return [anim_text]
        else:
            anim_text.set_visible(False)
            return []

    ani = FuncAnimation(fig, update_frame, frames=range(len(y_filas) + 2), interval=120, blit=True, repeat=False)
    
    # CONVERSIÓN A WEB: En lugar de plt.show(), lo pasamos a HTML/JS interactivo
    html_animacion = ani.to_jshtml()
    
    # Importante: cerrar la figura para liberar memoria del servidor
    plt.close(fig) 
    
    return html_animacion

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    # Ejecutamos la función y guardamos el código HTML generado
    codigo_corazon = generar_corazon_html()
    # Pasamos la variable al template
    return render_template('about.html', animacion=codigo_corazon)

if __name__ == '__main__':
    app.run(debug=True)