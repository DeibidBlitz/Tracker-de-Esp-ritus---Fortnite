from itertools import groupby
import io
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import qrcode
import re
import streamlit as str_lit
from supabase import create_client, Client

# --- CONFIGURACIÓN DE PÁGINA (DEBE SER LA PRIMERA LLAMADA DE STREAMLIT) ---
str_lit.set_page_config(
    page_title="Tracker de Espíritus", page_icon="✨", layout="wide"
)

# --- CONEXIÓN A SUPABASE ---
try:
    url: str = str_lit.secrets["supabase"]["url"]
    key: str = str_lit.secrets["supabase"]["key"]
    supabase: Client = create_client(url, key)
except Exception as e:
    supabase = None

# --- CONFIGURACIÓN DE CARPETAS Y ARCHIVOS ---
IMG_FOLDER = "imagenes"
IMAGEN_FONDO_EXPORT_PATH = os.path.join(IMG_FOLDER, "fondo_catalogo.png")
IMAGEN_FONDO_APP_PATH = os.path.join(IMG_FOLDER, "fondo_app.png")
IMAGEN_FONDO_CATEGORIA_PATH = os.path.join(IMG_FOLDER, "fondo_categoria.png")
IMAGEN_FONDO_VARIANTE_PATH = os.path.join(IMG_FOLDER, "fondo_variante.png")
CHECK_ICON_PATH = os.path.join(IMG_FOLDER, "check_verde.png")
CORONA_ICON_PATH = os.path.join(IMG_FOLDER, "corona.png")
LINKTREE_URL = "https://linktr.ee/deibid_blitz"

# --- ESTILOS CSS Y FONDO DE LA APP ---
if os.path.exists(IMAGEN_FONDO_APP_PATH):
  import base64

  with open(IMAGEN_FONDO_APP_PATH, "rb") as f:
    data = f.read()
  encoded_bg = base64.b64encode(data).decode()

  custom_css = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("data:image/webp;base64,{encoded_bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    div[data-baseweb="select"] {{
        max-width: 300px;
    }}
    div.stCheckbox {{
        background-color: rgba(30, 20, 10, 0.6);
        border: 1px solid rgba(255, 140, 0, 0.3);
        padding: 5px 10px;
        border-radius: 8px;
        margin-bottom: 5px;
    }}
    div.stCheckbox:hover {{
        border-color: rgba(255, 140, 0, 0.8);
    }}
    div.stButton > button {{
        background: linear-gradient(135deg, #ff8c00 0%, #ff6600 100%) !important;
        color: white !important;
        border: 1px solid #ffa500 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(135deg, #ffa500 0%, #ff7f00 100%) !important;
        border-color: #ffb732 !important;
        color: white !important;
    }}
    div.stButton > button:disabled {{
        background: rgba(50, 50, 50, 0.5) !important;
        border-color: rgba(100, 100, 100, 0.3) !important;
        color: #888 !important;
    }}
    </style>
    """
  str_lit.markdown(custom_css, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS DE SESIÓN ---
if "seleccionados" not in str_lit.session_state:
  str_lit.session_state.seleccionados = set()

if "dominados" not in str_lit.session_state:
  str_lit.session_state.dominados = set()

if "file_uploader_key" not in str_lit.session_state:
  str_lit.session_state.file_uploader_key = 0

if "ultimo_bytes_leidos" not in str_lit.session_state:
  str_lit.session_state.ultimo_bytes_leidos = None

if "mensaje_restauracion" not in str_lit.session_state:
  str_lit.session_state.mensaje_restauracion = None

if not os.path.exists(IMG_FOLDER):
  os.makedirs(IMG_FOLDER)


# --- FUNCIONES AUXILIARES ---
def es_proximo(nombre_archivo):
  return "proximo" in nombre_archivo.lower() or "prox_" in nombre_archivo.lower()


def obtener_titulo_categoria(nombre_archivo):
  partes = nombre_archivo.split("-")
  if len(partes) >= 2:
    return partes[1].replace("_", " ").title()
  return "General"


def obtener_variante(nombre_archivo):
  nombre_base = os.path.splitext(nombre_archivo)[0].lower()
  if "cazarecompensas" in nombre_base:
    return "Cazarecompensas"
  elif "dorado" in nombre_base:
    return "Dorado"
  elif "hacker" in nombre_base and ("botin" in nombre_base or "botín" in nombre_base):
    return "Hacker de Botín"
  elif "hacker" in nombre_base:
    return "Hacker"
  elif "dulce" in nombre_base or "truco" in nombre_base or "halloween" in nombre_base:
    return "Dulce o Truco"
  elif "patito" in nombre_base:
    return "Patito"
  else:
    return "Normal"


def obtener_nombre_limpio(nombre_base):
  categoria = obtener_titulo_categoria(nombre_base + ".png")
  variante = obtener_variante(nombre_base + ".png")
  
  if variante == "Normal":
    return categoria
  else:
    return f"{categoria} {variante}"


def generar_qr_respaldo_bytes(seleccionados, dominados, lista_todos_archivos):
  bin_sel = "".join(
      "1" if os.path.splitext(f)[0] in seleccionados else "0"
      for f in lista_todos_archivos
  )
  bin_dom = "".join(
      "1" if os.path.splitext(f)[0] in dominados else "0"
      for f in lista_todos_archivos
  )

  val_sel = int(bin_sel, 2) if bin_sel else 0
  val_dom = int(bin_dom, 2) if bin_dom else 0
  datos_qr = f"{val_sel:x},{val_dom:x}"

  qr_gen = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_M,
      box_size=10,
      border=4,
  )
  qr_gen.add_data(datos_qr)
  qr_gen.make(fit=True)
  img_qr = qr_gen.make_image(fill_color="black", back_color="white").convert("RGB")

  buf = io.BytesIO()
  img_qr.save(buf, format="PNG")
  return buf.getvalue()


def leer_progreso_desde_imagen(imagen_bytes, lista_todos_archivos):
  try:
    np_arr = np.frombuffer(imagen_bytes, np.uint8)
    img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img_cv)

    if data and "," in data:
      partes = data.split(",")
      val_sel = int(partes[0], 16)
      val_dom = int(partes[1], 16)

      total_archivos = len(lista_todos_archivos)
      bin_sel = bin(val_sel)[2:].zfill(total_archivos)
      bin_dom = bin(val_dom)[2:].zfill(total_archivos)

      todos_ids = [os.path.splitext(f)[0] for f in lista_todos_archivos]

      sel_recuperados = [
          todos_ids[i] for i, bit in enumerate(bin_sel) if bit == "1"
      ]
      dom_recuperados = [
          todos_ids[i] for i, bit in enumerate(bin_dom) if bit == "1"
      ]

      return sel_recuperados, dom_recuperados
  except Exception as e:
    print(f"Error leyendo QR compacto: {e}")
  return None, None


def generar_imagen_coleccion(
    lista_ordenada_archivos,
    seleccionados,
    dominados,
    todos_los_archivos_global,
    titulo_personalizado=None,
    usar_fondo_app=False,
    imagen_custom=None,
    mostrar_marcas=True,
    tipo_tarjeta="general",
    usuario_id=None,
):
  if not lista_ordenada_archivos:
    img_vacia = Image.new("RGBA", (400, 150), color=(20, 20, 20, 255))
    buf = io.BytesIO()
    img_vacia.save(buf, format="PNG")
    return buf.getvalue()

  columnas = 10
  ancho_celda = 90
  alto_celda = 110
  padding_lateral = 20
  padding_superior = 90
  filas = (len(lista_ordenada_archivos) // columnas) + 1

  ancho_total = (columnas * ancho_celda) + (padding_lateral * 2)
  alto_total = (filas * alto_celda) + padding_superior + 55

  if imagen_custom is not None:
    ruta_fondo = None
  elif usar_fondo_app and os.path.exists(IMAGEN_FONDO_APP_PATH):
    ruta_fondo = IMAGEN_FONDO_APP_PATH
  elif tipo_tarjeta == "categoria" and os.path.exists(IMAGEN_FONDO_CATEGORIA_PATH):
    ruta_fondo = IMAGEN_FONDO_CATEGORIA_PATH
  elif tipo_tarjeta == "variante" and os.path.exists(IMAGEN_FONDO_VARIANTE_PATH):
    ruta_fondo = IMAGEN_FONDO_VARIANTE_PATH
  else:
    ruta_fondo = IMAGEN_FONDO_EXPORT_PATH

  if imagen_custom is not None:
    fondo_original = Image.open(imagen_custom).convert("RGBA")
    img_final = fondo_original.resize((ancho_total, alto_total))
  elif ruta_fondo and os.path.exists(ruta_fondo):
    fondo_original = Image.open(ruta_fondo).convert("RGBA")
    img_final = fondo_original.resize((ancho_total, alto_total))
  else:
    img_final = Image.new(
        "RGBA", (ancho_total, alto_total), color=(20, 20, 20, 255)
    )

  capa_ui = Image.new("RGBA", (ancho_total, alto_total), (0, 0, 0, 0))
  d_ui = ImageDraw.Draw(capa_ui)

  d_ui.rectangle(
      [padding_lateral, 15, ancho_total - padding_lateral, 75],
      fill=(10, 40, 15, 230),
      outline=(0, 255, 100, 255),
      width=2,
  )

  for i in range(len(lista_ordenada_archivos)):
    x = padding_lateral + (i % columnas) * ancho_celda + 10
    y = padding_superior + (i // columnas) * alto_celda + 10
    nombre_base = os.path.splitext(lista_ordenada_archivos[i])[0]
    is_dom = nombre_base in dominados if mostrar_marcas else False

    if is_dom:
      d_ui.rectangle(
          [x - 5, y - 5, x + 75, y + 100],
          fill=(255, 215, 0, 50),
          outline=(255, 215, 0, 220),
          width=2,
      )
    else:
      d_ui.rectangle(
          [x - 5, y - 5, x + 75, y + 100],
          fill=(10, 30, 10, 160),
          outline=(0, 200, 80, 220),
          width=2,
      )

  img_final = Image.alpha_composite(img_final, capa_ui)

  qr_gen = qrcode.QRCode(
      version=1,
      error_correction=qrcode.constants.ERROR_CORRECT_M,
      box_size=2,
      border=1,
  )
  qr_gen.add_data(LINKTREE_URL)
  qr_gen.make(fit=True)
  img_qr_pil = qr_gen.make_image(fill_color="black", back_color="white").convert(
      "RGBA"
  )

  pos_qr_x = ancho_total - padding_lateral - img_qr_pil.width - 10
  pos_qr_y = alto_total - img_qr_pil.height - 15
  img_final.paste(img_qr_pil, (pos_qr_x, pos_qr_y), img_qr_pil)

  ruta_fuente = os.path.join(IMG_FOLDER, "BURBANK.ttf")
  try:
    font_principal = ImageFont.truetype(ruta_fuente, 28)
    font_id = ImageFont.truetype(ruta_fuente, 20)
    font_contador = ImageFont.truetype(ruta_fuente, 22)
    font_qr_msg = ImageFont.truetype(ruta_fuente, 13)
  except IOError:
    font_principal = ImageFont.load_default()
    font_id = ImageFont.load_default()
    font_contador = ImageFont.load_default()
    font_qr_msg = ImageFont.load_default()

  d = ImageDraw.Draw(img_final)

  texto_qr_msg = "¡Crea tu propia plantilla!"
  bbox_msg = d.textbbox((0, 0), texto_qr_msg, font=font_qr_msg)
  w_msg = bbox_msg[2] - bbox_msg[0]
  h_msg = bbox_msg[3] - bbox_msg[1]
  
  pos_msg_x = pos_qr_x + (img_qr_pil.width - w_msg) // 2
  pos_msg_y = pos_qr_y - h_msg - 5

  d.text((pos_msg_x + 1, pos_msg_y + 1), texto_qr_msg, fill=(0, 0, 0, 255), font=font_qr_msg)
  d.text((pos_msg_x, pos_msg_y), texto_qr_msg, fill=(255, 255, 255, 255), font=font_qr_msg)

  texto_titulo = (
      titulo_personalizado
      if titulo_personalizado
      else "MI COLECCIÓN DE ESPÍRITUS"
  )

  # Dibujar título principal a la izquierda
  d.text(
      (padding_lateral + 17, 30),
      texto_titulo,
      fill=(0, 0, 0, 255),
      font=font_principal,
  )
  d.text(
      (padding_lateral + 15, 28),
      texto_titulo,
      fill=(255, 255, 255, 255),
      font=font_principal,
  )

  # Dibujar ID centrado en medio si se proporciona
  if usuario_id and usuario_id.strip():
    texto_id_completo = f"ID: {usuario_id.strip()}"
    bbox_id = d.textbbox((0, 0), texto_id_completo, font=font_id)
    w_id = bbox_id[2] - bbox_id[0]
    pos_id_x = (ancho_total - w_id) // 2
    d.text((pos_id_x + 1, 32), texto_id_completo, fill=(0, 0, 0, 255), font=font_id)
    d.text((pos_id_x, 31), texto_id_completo, fill=(200, 220, 255, 255), font=font_id)

  total_items = len(lista_ordenada_archivos)
  
  if mostrar_marcas:
    obtenidos_totales = sum(
        1
        for f in lista_ordenada_archivos
        if os.path.splitext(f)[0] in seleccionados
    )
    dominados_totales = sum(
        1 for f in lista_ordenada_archivos if os.path.splitext(f)[0] in dominados
    )

    pos_x_base = ancho_total - padding_lateral - 215
    pos_y_iconos = 32
    pos_y_texto = 33

    img_check_mini = (
        Image.open(CHECK_ICON_PATH).convert("RGBA").resize((22, 22))
        if os.path.exists(CHECK_ICON_PATH)
        else None
    )
    img_corona_mini = (
        Image.open(CORONA_ICON_PATH).convert("RGBA").resize((24, 24))
        if os.path.exists(CORONA_ICON_PATH)
        else None
    )

    current_x = pos_x_base
    if img_check_mini:
      img_final.paste(img_check_mini, (current_x, pos_y_iconos), img_check_mini)
      current_x += 26
    else:
      d.text((current_x, pos_y_texto), "✓", fill=(0, 255, 100), font=font_contador)
      current_x += 20

    d.text(
        (current_x, pos_y_texto),
        f"{obtenidos_totales}/{total_items}",
        fill=(255, 255, 255),
        font=font_contador,
    )
    current_x += 90
    if img_corona_mini:
      img_final.paste(
          img_corona_mini, (current_x, pos_y_iconos - 2), img_corona_mini
      )
      current_x += 28
    else:
      d.text(
          (current_x, pos_y_texto), "👑", fill=(255, 215, 0), font=font_contador
      )
      current_x += 25

    d.text(
        (current_x, pos_y_texto),
        f"{dominados_totales}/{total_items}",
        fill=(255, 255, 255),
        font=font_contador,
    )

  img_check = (
      Image.open(CHECK_ICON_PATH).convert("RGBA").resize((26, 26))
      if os.path.exists(CHECK_ICON_PATH)
      else None
  )
  img_corona = (
      Image.open(CORONA_ICON_PATH).convert("RGBA").resize((32, 32))
      if os.path.exists(CORONA_ICON_PATH)
      else None
  )

  for i, archivo in enumerate(lista_ordenada_archivos):
    ruta = os.path.join(IMG_FOLDER, archivo)
    img_espiritu = Image.open(ruta).convert("RGBA").resize((70, 70))
    x = padding_lateral + (i % columnas) * ancho_celda + 10
    y = padding_superior + (i // columnas) * alto_celda + 10
    img_final.paste(img_espiritu, (x, y), img_espiritu)

    if mostrar_marcas:
      nombre_base = os.path.splitext(archivo)[0]
      is_checked = nombre_base in seleccionados
      is_dom = nombre_base in dominados

      if is_dom:
        d.rectangle(
            [x + 20, y + 73, x + 50, y + 97],
            fill=(50, 40, 0, 220),
            outline=(255, 215, 0),
            width=2,
        )
        if img_corona:
          img_final.paste(img_corona, (x + 19, y + 70), img_corona)
        else:
          d.text((x + 24, y + 75), "👑", fill=(255, 215, 0))
      elif is_checked:
        d.rectangle(
            [x + 22, y + 75, x + 48, y + 95], outline=(0, 255, 100), width=1
        )
        if img_check:
          img_final.paste(img_check, (x + 22, y + 73), img_check)
        else:
          d.text((x + 28, y + 76), "✓", fill=(0, 255, 100))

  buf = io.BytesIO()
  img_final.save(buf, format="PNG")
  return buf.getvalue()


# --- CARGA Y PROCESAMIENTO INICIAL ---
if os.path.exists(IMG_FOLDER):
  archivos_ignorar = {
      "check_verde.png",
      "corona.png",
      "fondo_app.png",
      "fondo_catalogo.png",
      "fondo_categoria.png",
      "fondo_variante.png",
  }
  archivos_crudos = sorted([
      f
      for f in os.listdir(IMG_FOLDER)
      if f.lower().endswith(".png")
      and not f.startswith("num_")
      and not f.lower().startswith("fondo_")
      and f.lower() not in archivos_ignorar
  ])
  archivos_ordenados = list(archivos_crudos)
  
  archivos_activos_tarjeta = [f for f in archivos_ordenados if not es_proximo(f)]
  todos_los_ids = [os.path.splitext(f)[0] for f in archivos_ordenados]
  todos_los_ids_activos = [os.path.splitext(f)[0] for f in archivos_activos_tarjeta]

  categorias_disponibles = []
  for f in archivos_crudos:
    cat = obtener_titulo_categoria(f)
    if cat not in categorias_disponibles:
      categorias_disponibles.append(cat)

  cat_to_ids = {}
  variantes_disponibles = ["Normal", "Dorado", "Hacker", "Hacker de Botín", "Cazarecompensas", "Dulce o Truco", "Patito"]
  var_to_ids = {v: [] for v in variantes_disponibles}

  for f in archivos_crudos:
    cat = obtener_titulo_categoria(f)
    f_id = os.path.splitext(f)[0]
    if cat not in cat_to_ids:
      cat_to_ids[cat] = []
    cat_to_ids[cat].append(f_id)
    var = obtener_variante(f)
    if var in var_to_ids:
      var_to_ids[var].append(f_id)

  # --- BARRA LATERAL ---
  with str_lit.sidebar:
    str_lit.header("⚙️ Opciones")

    # --- SECCIÓN DE SUPABASE EN BARRA LATERAL ---
    if supabase:
      with str_lit.expander("☁️ Guardar en la Nube (Supabase)"):
        user_cloud = str_lit.text_input("Usuario Fortnite:", key="input_user_sb")
        if str_lit.button("Guardar en Supabase", use_container_width=True):
          if user_cloud:
            try:
              data_insert = {
                  "usuario": user_cloud,
                  "puntuacion": len(str_lit.session_state.seleccionados)
              }
              supabase.table("progreso_usuarios").insert(data_insert).execute()
              str_lit.success("¡Progreso registrado en la nube!")
            except Exception as err:
              str_lit.error(f"Error al guardar: {err}")
          else:
            str_lit.warning("Escribe un nombre de usuario.")

        if str_lit.button("Cargar Líderes", use_container_width=True):
          try:
            res_sb = supabase.table("progreso_usuarios").select("*").execute()
            str_lit.write(res_sb.data)
          except Exception as err:
            str_lit.error(f"Error al cargar: {err}")

    str_lit.markdown("**Modo de Visualización**")
    modo_visualizacion = str_lit.selectbox(
        "Modo", ["Por Categoría", "Por Variante"], label_visibility="collapsed"
    )

    str_lit.markdown("---")

    is_all_checked = all(
        id_esp in str_lit.session_state.seleccionados for id_esp in todos_los_ids_activos
    )
    is_all_dom = all(
        id_esp in str_lit.session_state.dominados for id_esp in todos_los_ids_activos
    )


    def toggle_global_chk():
      current_all = all(
          id_esp in str_lit.session_state.seleccionados
          for id_esp in todos_los_ids_activos
      )
      if current_all:
        for id_esp in todos_los_ids_activos:
          str_lit.session_state.seleccionados.discard(id_esp)
          str_lit.session_state.dominados.discard(id_esp)
      else:
        for id_esp in todos_los_ids_activos:
          str_lit.session_state.seleccionados.add(id_esp)


    str_lit.checkbox(
        "✅ Marcar Todos",
        value=is_all_checked,
        key="global_chk",
        on_change=toggle_global_chk,
    )


    def toggle_global_dom():
      current_all = all(
          id_esp in str_lit.session_state.dominados for id_esp in todos_los_ids_activos
      )
      if current_all:
        for id_esp in todos_los_ids_activos:
          str_lit.session_state.dominados.discard(id_esp)
      else:
        for id_esp in todos_los_ids_activos:
          str_lit.session_state.seleccionados.add(id_esp)
          str_lit.session_state.dominados.add(id_esp)


    str_lit.checkbox(
        "👑 Dominar Todos",
        value=is_all_dom,
        key="global_dom",
        on_change=toggle_global_dom,
    )
    str_lit.markdown("---")

    with str_lit.expander("📌 Marcar por categoría"):
      for cat in categorias_disponibles:
        ids_cat = [i for i in cat_to_ids[cat] if not es_proximo(i + ".png")]
        if not ids_cat:
          continue
        cat_checked_all = all(
            id_esp in str_lit.session_state.seleccionados for id_esp in ids_cat
        )

        def make_toggle_cat_chk(c_ids
