<<<<<<< HEAD
import streamlit as st
import os
from itertools import groupby
from PIL import Image, ImageDraw
import io

IMG_FOLDER = "imagenes"

# --- DICCIONARIO DE NOMBRES ---
MAPA_NOMBRES = {
    "11-PUNTO_CERO-01_Punto-Cero_Normal": "Punto Cero",
    "11-PUNTO_CERO-02_Punto-Cero_Dorado": "Punto Cero Dorado",
    "11-PUNTO_CERO-03_Punto-Cero_Golosina": "Punto Cero Golosina",
    "11-PUNTO_CERO-04_Punto-Cero_Galáctico": "Punto Cero Galáctico",
    "12-PALITO_DE_PEZ-01_Palito-De_Pez_Normal": "Palito De Pez",
    "12-PALITO_DE_PEZ-02_Palito-De_Pez_Dorado": "Palito De Pez Dorado",
    "12-PALITO_DE_PEZ-03_Palito-De_Pez_Golosina": "Palito De Pez Golosina",
    "12-PALITO_DE_PEZ-04_Palito-De_Pez_Galáctico": "Palito De Pez Galáctico",
    "18-LOS_SIETE-01_Los_Siete_Normal": "Los Siete",
    "18-LOS_SIETE-02_Los_Siete_Dorado": "Los Siete Dorado",
    "18-LOS_SIETE-03_Los_Siete_Golosina": "Los Siete Golosina",
    "18-LOS_SIETE-04_Los_Siete_Galáctico": "Los Siete Galáctico",
    "18-LOS_SIETE-05_Los_Siete_Holo": "Los Siete Holo",
}

st.set_page_config(page_title="Tracker de Espíritus", layout="wide")
st.title("Tracker de Espíritus - Fortnite")

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set()

# --- GENERADOR DE IMAGEN (Minimalista) ---
def generar_imagen_coleccion(todos_los_archivos, seleccionados):
    columnas = 10
    ancho_celda = 90
    alto_celda = 110
    filas = (len(todos_los_archivos) // columnas) + 1
    
    img_final = Image.new('RGB', (columnas * ancho_celda, filas * alto_celda), color=(20, 20, 20))
    d = ImageDraw.Draw(img_final)
    
    for i, archivo in enumerate(todos_los_archivos):
        ruta = os.path.join(IMG_FOLDER, archivo)
        img_espiritu = Image.open(ruta).resize((70, 70))
        
        x = (i % columnas) * ancho_celda + 10
        y = (i // columnas) * alto_celda + 10
        
        img_final.paste(img_espiritu, (x, y))
        
        nombre_base = os.path.splitext(archivo)[0]
        
        # Estado basado en ID único
        is_checked = nombre_base in seleccionados
        color_cuadro = (0, 255, 0) if is_checked else (100, 100, 100)
        
        d.rectangle([x + 25, y + 75, x + 45, y + 95], outline=color_cuadro, width=2)
        if is_checked:
            d.text((x + 30, y + 78), "✓", fill=color_cuadro)
            
    buf = io.BytesIO()
    img_final.save(buf, format="PNG")
    return buf.getvalue()

def obtener_titulo_categoria(nombre_archivo):
    return nombre_archivo.split('-')[1].replace("_", " ")

# --- LÓGICA PRINCIPAL ---
if os.path.exists(IMG_FOLDER):
    archivos = sorted([f for f in os.listdir(IMG_FOLDER) if f.endswith('.png')])
    
    for categoria, grupo in groupby(archivos, key=obtener_titulo_categoria):
        st.subheader(categoria.title())
        lista_grupo = list(grupo)
        cols = st.columns(5)
        
        for i, archivo in enumerate(lista_grupo):
            nombre_base = os.path.splitext(archivo)[0]
            
            # Nombre limpio para la web
            nombre_mostrado = MAPA_NOMBRES.get(nombre_base, nombre_base.split('_', 1)[-1].replace("-", " ").replace("_", " ").title())
            
            with cols[i % 5]:
                st.image(f"{IMG_FOLDER}/{archivo}", width=100)
                
                # Identificador único para el estado
                is_checked = nombre_base in st.session_state.seleccionados
                
                etiqueta = f"{'✅' if is_checked else '⬜'} {nombre_mostrado}"
                
                if st.button(etiqueta, key=f"btn_{nombre_base}", use_container_width=True, type="primary" if is_checked else "secondary"):
                    if is_checked:
                        st.session_state.seleccionados.remove(nombre_base)
                    else:
                        st.session_state.seleccionados.add(nombre_base)
                    st.rerun()

    st.divider()
    if st.session_state.seleccionados:
        img_bytes = generar_imagen_coleccion(archivos, st.session_state.seleccionados)
        st.download_button(
            label="💾 Descargar Catálogo Visual",
            data=img_bytes,
            file_name="catalogo_espiritus.png",
            mime="image/png"
        )
    else:
        st.info("Selecciona algunos espíritus para poder descargar la imagen.")
else:
=======
import streamlit as st
import os
from itertools import groupby

IMG_FOLDER = "imagenes"

# --- DICCIONARIO DE NOMBRES ---
# Aquí controlas los casos especiales o nombres complejos.
# Si el nombre está aquí, el código usará el valor que definas sin limpiar nada.
MAPA_NOMBRES = {
    "11-PUNTO_CERO-01_Punto-Cero_Normal": "Punto Cero",
    "11-PUNTO_CERO-02_Punto-Cero_Dorado": "Punto Cero Dorado",
    "11-PUNTO_CERO-03_Punto-Cero_Golosina": "Punto Cero Golosina",
    "11-PUNTO_CERO-04_Punto-Cero_Galáctico": "Punto Cero Galáctico",
    "12-PALITO_DE_PEZ-01_Palito-De_Pez_Normal": "Palito De Pez",
    "12-PALITO_DE_PEZ-02_Palito-De_Pez_Dorado": "Palito De Pez Dorado",
    "12-PALITO_DE_PEZ-03_Palito-De_Pez_Golosina": "Palito De Pez Golosina",
    "12-PALITO_DE_PEZ-04_Palito-De_Pez_Galáctico": "Palito De Pez Galáctico",
    
}

st.set_page_config(page_title="Tracker de Espíritus", layout="wide")
st.title("Tracker de Espíritus - Fortnite")

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set()

def obtener_titulo_categoria(nombre_archivo):
    return nombre_archivo.split('-')[1].replace("_", " ")

if os.path.exists(IMG_FOLDER):
    archivos = sorted([f for f in os.listdir(IMG_FOLDER) if f.endswith('.png')])
    
    for categoria, grupo in groupby(archivos, key=obtener_titulo_categoria):
        st.subheader(categoria.title())
        
        lista_grupo = list(grupo)
        num_columnas = 5
        cols = st.columns(num_columnas)
        
        for i, archivo in enumerate(lista_grupo):
            nombre_base = os.path.splitext(archivo)[0]
            
            # --- LÓGICA DE DICCIONARIO Y AUTOMATIZACIÓN ---
            if nombre_base in MAPA_NOMBRES:
                nombre_mostrado = MAPA_NOMBRES[nombre_base]
            else:
                # Automatización para el resto
                parte_nombre = nombre_base.split('_', 1)[1] if '_' in nombre_base else nombre_base
                nombre_mostrado = parte_nombre.replace("-", " ").replace("_", " ").title()
                
                # LIMPIEZA AUTOMÁTICA: Si termina en "Normal", la quitamos
                if nombre_mostrado.endswith(" Normal"):
                    nombre_mostrado = nombre_mostrado.replace(" Normal", "")
            
            with cols[i % num_columnas]:
                st.image(f"{IMG_FOLDER}/{archivo}", width=100)
                
                is_checked = nombre_mostrado in st.session_state.seleccionados
                etiqueta = f"✅ {nombre_mostrado}" if is_checked else f"⬜ {nombre_mostrado}"
                
                if st.button(etiqueta, key=f"btn_{nombre_base}", use_container_width=True, type="primary" if is_checked else "secondary"):
                    if nombre_mostrado in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(nombre_mostrado)
                    else:
                        st.session_state.seleccionados.add(nombre_mostrado)
                    st.rerun()
else:
>>>>>>> 75f7b07297edf38e84148fabe5dcc1012107d89b
    st.warning("Aún no he encontrado la carpeta de imágenes.")