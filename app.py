import streamlit as str_lit
import os
from itertools import groupby
from PIL import Image, ImageDraw, ImageFont
import io

IMG_FOLDER = "imagenes"
IMAGEN_FONDO_PATH = os.path.join(IMG_FOLDER, "fondo_catalogo.png")
CHECK_ICON_PATH = os.path.join(IMG_FOLDER, "check_verde.png")
CORONA_ICON_PATH = os.path.join(IMG_FOLDER, "corona.png")

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

if 'dominados' not in str_lit.session_state:
    str_lit.session_state.dominados = set()

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def obtener_titulo_categoria(nombre_archivo):
    return nombre_archivo.split('-')[1].replace("_", " ")

def generar_imagen_coleccion(lista_ordenada_archivos, seleccionados, dominados):
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
    
    # Barra superior para la interfaz
    d_ui.rectangle([padding_lateral, 15, ancho_total - padding_lateral, 75], fill=(0, 0, 0, 190))
    
    for i in range(len(lista_ordenada_archivos)):
        x = padding_lateral + (i % columnas) * ancho_celda + 10
        y = padding_superior + (i // columnas) * alto_celda + 10
        d_ui.rectangle([x - 5, y - 5, x + 75, y + 100], fill=(0, 0, 0, 100))
        
    img_final = Image.alpha_composite(img_final, capa_ui)
    
    # Carga de la fuente oficial Burbank
    ruta_fuente = os.path.join(IMG_FOLDER, "BURBANK.ttf")
    try:
        font_principal = ImageFont.truetype(ruta_fuente, 32)
        font_contador = ImageFont.truetype(ruta_fuente, 30)
    except IOError:
        font_principal = ImageFont.load_default()
        font_contador = ImageFont.load_default()

    d = ImageDraw.Draw(img_final)

    # TÍTULO PROCEDURAL
    texto_titulo = "MI COLECCIÓN DE ESPÍRITUS"
    pos_x_titulo = padding_lateral + 20
    pos_y_titulo = 25
    
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        d.text((pos_x_titulo + dx, pos_y_titulo + dy), texto_titulo, fill=(0, 0, 0, 255), font=font_principal)
    d.text((pos_x_titulo, pos_y_titulo), texto_titulo, fill=(255, 255, 255, 255), font=font_principal)

    # CONTADOR DINÁMICO PROCEDURAL (Suma tanto obtenidos como dominados)
    total_items = len(lista_ordenada_archivos)
    obtenidos_totales = sum(1 for f in lista_ordenada_archivos if (os.path.splitext(f)[0] in seleccionados) or (os.path.splitext(f)[0] in dominados))
    texto_progreso = f"{obtenidos_totales}/{total_items}"
    
    pos_x_texto = ancho_total - padding_lateral - 120
    pos_y_texto = 28
    
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        d.text((pos_x_texto + dx, pos_y_texto + dy), texto_progreso, fill=(0, 0, 0, 255), font=font_contador)
    d.text((pos_x_texto, pos_y_texto), texto_progreso, fill=(0, 255, 120, 255), font=font_contador)

    img_check = None
    if os.path.exists(CHECK_ICON_PATH):
        img_check = Image.open(CHECK_ICON_PATH).convert('RGBA').resize((26, 26))

    img_corona = None
    if os.path.exists(CORONA_ICON_PATH):
        img_corona = Image.open(CORONA_ICON_PATH).convert('RGBA').resize((26, 26))

    for i, archivo in enumerate(lista_ordenada_archivos):
        ruta = os.path.join(IMG_FOLDER, archivo)
        img_espiritu = Image.open(ruta).convert('RGBA').resize((70, 70))
        
        x = padding_lateral + (i % columnas) * ancho_celda + 10
        y = padding_superior + (i // columnas) * alto_celda + 10
        
        img_final.paste(img_espiritu, (x, y), img_espiritu)
        
        nombre_base = os.path.splitext(archivo)[0]
        is_checked = nombre_base in seleccionados
        is_dom = nombre_base in dominados
        
        # Un solo recuadro minimalista y centrado debajo de cada espíritu
        d.rectangle([x + 22, y + 75, x + 48, y + 95], outline=(120, 120, 120), width=1)
        
        if is_dom:
            # Si está dominado, se muestra la corona limpia
            if img_corona:
                img_final.paste(img_corona, (x + 22, y + 73), img_corona)
            else:
                d.text((x + 26, y + 76), "👑", fill=(255, 215, 0))
        elif is_checked:
            # Si solo está obtenido, se muestra el check verde
            if img_check:
                img_final.paste(img_check, (x + 22, y + 73), img_check)
            else:
                d.text((x + 28, y + 76), "✓", fill=(0, 255, 120))
            
    buf = io.BytesIO()
    img_final.save(buf, format="PNG")
    return buf.getvalue()

if os.path.exists(IMG_FOLDER):
    archivos_crudos = sorted([f for f in os.listdir(IMG_FOLDER) if f.endswith('.png') and not f.startswith('num_') and f not in ['fondo_catalogo.png', 'check_verde.png', 'corona.png', 'titulo_banner.png', 'fuente_fallback.ttf']])
    
    archivos_ordenados = []
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        archivos_ordenados.extend(list(grupo))
    
    for categoria, grupo in groupby(archivos_crudos, key=obtener_titulo_categoria):
        lista_grupo = list(grupo)
        ids_grupo = [os.path.splitext(f)[0] for f in lista_grupo]
        
        # Validar si todos están seleccionados o dominados en esta categoría
        todos_seleccionados = all(id_esp in str_lit.session_state.seleccionados for id_esp in ids_grupo)
        todos_dominados = all(id_esp in str_lit.session_state.dominados for id_esp in ids_grupo)
        
        # Diseño de cabecera de categoría con título y controles maestros independientes
        col_tit, col_btn_chk, col_btn_dom = str_lit.columns([6, 3, 3])
        
        with col_tit:
            str_lit.markdown(f"### {categoria.title()}")
            
        with col_btn_chk:
            def toggle_cat_chk(ids=ids_grupo):
                current_all = all(id_esp in str_lit.session_state.seleccionados for id_esp in ids)
                if current_all:
                    for id_esp in ids:
                        str_lit.session_state.seleccionados.discard(id_esp)
                        str_lit.session_state.dominados.discard(id_esp)
                else:
                    for id_esp in ids:
                        str_lit.session_state.seleccionados.add(id_esp)

            str_lit.checkbox("✅ Todos", value=todos_seleccionados, key=f"cat_chk_{categoria}", on_change=toggle_cat_chk)
            
        with col_btn_dom:
            def toggle_cat_dom(ids=ids_grupo):
                current_all = all(id_esp in str_lit.session_state.dominados for id_esp in ids)
                if current_all:
                    for id_esp in ids:
                        str_lit.session_state.dominados.discard(id_esp)
                else:
                    for id_esp in ids:
                        str_lit.session_state.seleccionados.add(id_esp) # Asegurar que estén seleccionados también
                        str_lit.session_state.dominados.add(id_esp)

            str_lit.checkbox("👑 Todos", value=todos_dominados, key=f"cat_dom_{categoria}", on_change=toggle_cat_dom)
        
        cols = str_lit.columns(5)
        
        for i, archivo in enumerate(lista_grupo):
            nombre_base = os.path.splitext(archivo)[0]
            
            nombre_crudo = MAPA_NOMBRES.get(nombre_base, nombre_base.split('_', 1)[-1].replace("-", " ").replace("_", " ").title())
            nombre_mostrado = nombre_crudo.replace("Normal", "").strip()
            
            with cols[i % 5]:
                str_lit.image(f"{IMG_FOLDER}/{archivo}", width=100)
                
                # Nombre del espíritu conservado claramente
                str_lit.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 5px;'>{nombre_mostrado}</div>", unsafe_allow_html=True)
                
                is_checked = nombre_base in str_lit.session_state.seleccionados
                is_dom = nombre_base in str_lit.session_state.dominados
                
                # Controles web limpios para alternar entre obtenido y dominado individualmente
                c_btn1, c_btn2 = str_lit.columns(2)
                
                with c_btn1:
                    etiqueta_chk = "✅" if is_checked else "⬜"
                    if str_lit.button(etiqueta_chk, key=f"chk_{nombre_base}", use_container_width=True):
                        if is_checked:
                            str_lit.session_state.seleccionados.remove(nombre_base)
                            if nombre_base in str_lit.session_state.dominados:
                                str_lit.session_state.dominados.remove(nombre_base)
                        else:
                            str_lit.session_state.seleccionados.add(nombre_base)
                        str_lit.rerun()
                
                with c_btn2:
                    etiqueta_dom = "👑" if is_dom else "⬚"
                    if is_checked:
                        if str_lit.button(etiqueta_dom, key=f"dom_{nombre_base}", use_container_width=True):
                            if is_dom:
                                str_lit.session_state.dominados.remove(nombre_base)
                            else:
                                str_lit.session_state.dominados.add(nombre_base)
                            str_lit.rerun()
                    else:
                        str_lit.button("🔒", key=f"dom_{nombre_base}", disabled=True, use_container_width=True)

    str_lit.divider()
    if str_lit.session_state.seleccionados or str_lit.session_state.dominados:
        img_bytes = generar_imagen_coleccion(archivos_ordenados, str_lit.session_state.seleccionados, str_lit.session_state.dominados)
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
