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
    st.warning("Aún no he encontrado la carpeta de imágenes.")