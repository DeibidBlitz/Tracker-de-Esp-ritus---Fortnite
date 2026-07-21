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
    "20-VINI_JR-01_Vini_Jr_Normal": "Vini Jr",
}

st.set_page_config(page_title="Tracker de Espíritus", layout="wide")
st.title("Tracker de Espíritus - Fortnite")

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set()

def obtener_titulo_categoria(nombre_archivo):
    return nombre_archivo.split('-')[1].replace("_", " ")

# --- GENERADOR DE IMAGEN (Sincronizado con el orden visual por categorías) ---
def generar_imagen_coleccion(lista_ordenada_archivos, seleccionados):
    columnas = 10
    ancho_celda = 90
    alto_celda = 110
    filas = (len(lista_ordenada_archivos) // columnas) + 1
    
    img_final = Image.new('RGB', (columnas * ancho_celda, filas * alto_celda), color=(20, 20, 20))
    d = ImageDraw.Draw(img_final)
    
    for i, archivo in enumerate(lista_ordenada_archivos):
        ruta = os.path.join(IMG_FOLDER, archivo)
        img_espiritu = Image.open(ruta).resize((70, 70))
        
        x = (i % columnas) * ancho_celda + 10
        y = (i // columnas) * alto_celda + 10
        
        img_final.paste(img_espiritu, (x, y))
        
        nombre_base = os.path.splitext(archivo)[0]
        
        is_checked = nombre_base in seleccionados
        color_cuadro = (0, 255, 0) if is_checked else (100, 100, 100)
        
        d.rectangle([x + 25, y + 75, x + 45, y + 95], outline=color_cuadro, width=2)
        if is_checked:
            d.text((x + 30, y + 78), "✓", fill=color_cuadro)
            
    buf = io.BytesIO()
    img_final.save(buf, format="PNG")
    return buf.getvalue()

# --- LÓGICA PRINCIPAL ---
if os.path.exists(IMG_FOLDER):
    archivos_crudos = sorted([f for f in os.listdir(IMG_FOLDER) if f.endswith('.png')])
    
    # Reconstruimos la misma lista ordenada exactamente como se muestra en pantalla por categoría
    archivos_ordenados = []
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        archivos_ordenados.extend(list(grupo))
    
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        lista_grupo = list(grupo)
        ids_grupo = [os.path.splitext(f)[0] for f in lista_grupo]
        
        num_seleccionados = sum(1 for id_esp in ids_grupo if id_esp in st.session_state.seleccionados)
        todos_seleccionados = (num_seleccionados == len(ids_grupo))
        
        # --- Cabecera de Categoría con Checkbox sincronizado ---
        col_tit, col_chk = st.columns([2, 10])
        with col_tit:
            def toggle_categoria(ids=ids_grupo):
                current_all = all(id_esp in st.session_state.seleccionados for id_esp in ids)
                if current_all:
                    for id_esp in ids:
                        st.session_state.seleccionados.discard(id_esp)
                else:
                    for id_esp in ids:
                        st.session_state.seleccionados.add(id_esp)

            st.checkbox(
                f"**{categoria.title()}**", 
                value=todos_seleccionados, 
                key=f"cat_chk_{categoria}",
                on_change=toggle_categoria
            )
        
        # --- CUADRÍCULA DE ESPÍRITUS ---
        cols = st.columns(5)
        
        for i, archivo in enumerate(lista_grupo):
            nombre_base = os.path.splitext(archivo)[0]
            
            nombre_crudo = MAPA_NOMBRES.get(nombre_base, nombre_base.split('_', 1)[-1].replace("-", " ").replace("_", " ").title())
            nombre_mostrado = nombre_crudo.replace("Normal", "").strip()
            
            with cols[i % 5]:
                st.image(f"{IMG_FOLDER}/{archivo}", width=100)
                
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
        # Pasamos la lista que respeta el orden visual de las categorías
        img_bytes = generar_imagen_coleccion(archivos_ordenados, st.session_state.seleccionados)
        st.download_button(
            label="💾 Descargar Catálogo Visual",
            data=img_bytes,
            file_name="catalogo_espiritus.png",
            mime="image/png"
        )
    else:
        st.info("Selecciona algunos espíritus para poder descargar la imagen.")
else:
    st.warning("Aún no he encontrado la carpeta de imágenes.")
