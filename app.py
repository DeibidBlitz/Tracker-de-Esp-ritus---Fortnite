import streamlit as str_lit
import os
from itertools import groupby
from PIL import Image, ImageDraw, ImageFont
import io

IMG_FOLDER = "imagenes"
IMAGEN_FONDO_PATH = os.path.join(IMG_FOLDER, "fondo_catalogo.png")
TITULO_IMAGEN_PATH = os.path.join(IMG_FOLDER, "titulo_banner.png")
CHECK_ICON_PATH = os.path.join(IMG_FOLDER, "check_verde.png")

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

str_lit.set_page_config(page_title="Tracker de Espíritus", layout="wide")
str_lit.title("Tracker de Espíritus - Fortnite")

if 'seleccionados' not in str_lit.session_state:
    str_lit.session_state.seleccionados = set()

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def obtener_titulo_categoria(nombre_archivo):
    return nombre_archivo.split('-')[1].replace("_", " ")

def generar_imagen_coleccion(lista_ordenada_archivos, seleccionados):
    columnas = 10
    ancho_celda = 90
    alto_celda = 110
    
    padding_lateral = 20
    padding_superior = 90 
    
    filas = (len(lista_ordenada_archivos) // columnas) + 1
    
    ancho_total = (columnas * ancho_celda) + (padding_lateral * 2)
    alto_total = (filas * alto_celda) + padding_superior + 20
    
    if os.path.exists(IMAGEN_FONDO_PATH):
        fondo_original = Image.open(IMAGEN_FONDO_PATH).convert('RGBA')
        img_final = fondo_original.resize((ancho_total, alto_total))
    else:
        img_final = Image.new('RGBA', (ancho_total, alto_total), color=(20, 20, 20, 255))
        
    capa_ui = Image.new('RGBA', (ancho_total, alto_total), (0, 0, 0, 0))
    d_ui = ImageDraw.Draw(capa_ui)
    
    d_ui.rectangle([padding_lateral, 15, ancho_total - padding_lateral, 75], fill=(0, 0, 0, 190))
    
    for i in range(len(lista_ordenada_archivos)):
        x = padding_lateral + (i % columnas) * ancho_celda + 10
        y = padding_superior + (i // columnas) * alto_celda + 10
        d_ui.rectangle([x - 5, y - 5, x + 75, y + 100], fill=(0, 0, 0, 100))
        
    img_final = Image.alpha_composite(img_final, capa_ui)
    
    # Pegar la imagen del título principal
    if os.path.exists(TITULO_IMAGEN_PATH):
        img_titulo = Image.open(TITULO_IMAGEN_PATH).convert('RGBA')
        h_proporcional = 40
        w_proporcional = int(img_titulo.width * (h_proporcional / img_titulo.height))
        img_titulo = img_titulo.resize((w_proporcional, h_proporcional))
        img_final.paste(img_titulo, (padding_lateral + 20, 26), img_titulo)

    # -------------------------------------------------------------
    # NUEVO PARADIGMA: Contador dinámico con fuente vectorial segura
    # -------------------------------------------------------------
    total_items = len(lista_ordenada_archivos)
    obtenidos = sum(1 for f in lista_ordenada_archivos if os.path.splitext(f)[0] in seleccionados)
    texto_progreso = f"{obtenidos}/{total_items}"
    
    # Rutas comunes de fuentes negritas según sistema operativo (Linux para Streamlit Cloud, Windows para local)
    rutas_fuentes = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux / Streamlit Cloud
        "C:/Windows/Fonts/arialbd.ttf",                          # Windows Local (alternativa segura)
        "Arial"
    ]
    
    font_contador = None
    for ruta_f in rutas_fuentes:
        try:
            font_contador = ImageFont.truetype(ruta_f, 26)
            break
        except IOError:
            continue
            
    if font_contador is None:
        font_contador = ImageFont.load_default()

    d = ImageDraw.Draw(img_final)
    pos_x_texto = ancho_total - padding_lateral - 110
    pos_y_texto = 30
    
    # Dibujar contorno negro múltiple (Esimula borde grueso estilo Fortnite)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        d.text((pos_x_texto + dx, pos_y_texto + dy), texto_progreso, fill=(0, 0, 0, 255), font=font_contador)
    
    # Texto principal encima (Verde brillante característico)
    d.text((pos_x_texto, pos_y_texto), texto_progreso, fill=(0, 255, 120, 255), font=font_contador)
    # -------------------------------------------------------------

    img_check = None
    if os.path.exists(CHECK_ICON_PATH):
        img_check = Image.open(CHECK_ICON_PATH).convert('RGBA').resize((26, 26))

    for i, archivo in enumerate(lista_ordenada_archivos):
        ruta = os.path.join(IMG_FOLDER, archivo)
        img_espiritu = Image.open(ruta).convert('RGBA').resize((70, 70))
        
        x = padding_lateral + (i % columnas) * ancho_celda + 10
        y = padding_superior + (i // columnas) * alto_celda + 10
        
        img_final.paste(img_espiritu, (x, y), img_espiritu)
        
        nombre_base = os.path.splitext(archivo)[0]
        is_checked = nombre_base in seleccionados
        
        d.rectangle([x + 22, y + 75, x + 48, y + 95], outline=(120, 120, 120), width=1)
        
        if is_checked:
            if img_check:
                img_final.paste(img_check, (x + 22, y + 73), img_check)
            else:
                d.rectangle([x + 22, y + 75, x + 48, y + 95], outline=(0, 255, 120), width=2)
                d.text((x + 28, y + 76), "✓", fill=(0, 255, 120))
            
    buf = io.BytesIO()
    img_final.save(buf, format="PNG")
    return buf.getvalue()

if os.path.exists(IMG_FOLDER):
    # Excluimos de la lista de espíritus los archivos de UI y los antiguos prefijos numéricos si quedaron por ahí
    archivos_crudos = sorted([f for f in os.listdir(IMG_FOLDER) if f.endswith('.png') and not f.startswith('num_') and f not in ['fondo_catalogo.png', 'check_verde.png', 'titulo_banner.png', 'fuente_fallback.ttf']])
    
    archivos_ordenados = []
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        archivos_ordenados.extend(list(grupo))
    
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        lista_grupo = list(grupo)
        ids_grupo = [os.path.splitext(f)[0] for f in lista_grupo]
        
        num_seleccionados = sum(1 for id_esp in ids_grupo if id_esp in str_lit.session_state.seleccionados)
        todos_seleccionados = (num_seleccionados == len(ids_grupo))
        
        col_tit, col_chk = str_lit.columns([2, 10])
        with col_tit:
            def toggle_categoria(ids=ids_grupo):
                current_all = all(id_esp in str_lit.session_state.seleccionados for id_esp in ids)
                if current_all:
                    for id_esp in ids:
                        str_lit.session_state.seleccionados.discard(id_esp)
                else:
                    for id_esp in ids:
                        str_lit.session_state.seleccionados.add(id_esp)

            str_lit.checkbox(
                f"**{categoria.title()}**", 
                value=todos_seleccionados, 
                key=f"cat_chk_{categoria}",
                on_change=toggle_categoria
            )
        
        cols = str_lit.columns(5)
        
        for i, archivo in enumerate(lista_grupo):
            nombre_base = os.path.splitext(archivo)[0]
            
            nombre_crudo = MAPA_NOMBRES.get(nombre_base, nombre_base.split('_', 1)[-1].replace("-", " ").replace("_", " ").title())
            nombre_mostrado = nombre_crudo.replace("Normal", "").strip()
            
            with cols[i % 5]:
                str_lit.image(f"{IMG_FOLDER}/{archivo}", width=100)
                
                is_checked = nombre_base in str_lit.session_state.seleccionados
                etiqueta = f"{'✅' if is_checked else '⬜'} {nombre_mostrado}"
                
                if str_lit.button(etiqueta, key=f"btn_{nombre_base}", use_container_width=True, type="primary" if is_checked else "secondary"):
                    if is_checked:
                        str_lit.session_state.seleccionados.remove(nombre_base)
                    else:
                        str_lit.session_state.seleccionados.add(nombre_base)
                    str_lit.rerun()

    str_lit.divider()
    if str_lit.session_state.seleccionados:
        img_bytes = generar_imagen_coleccion(archivos_ordenados, str_lit.session_state.seleccionados)
        str_lit.download_button(
            label="💾 Descargar Catálogo Visual",
            data=img_bytes,
            file_name="catalogo_espiritus.png",
            mime="image/png"
        )
    else:
        str_lit.info("Selecciona algunos espíritus para poder descargar la imagen.")
else:
    str_lit.warning("Aún no he encontrado la carpeta de imágenes.")
