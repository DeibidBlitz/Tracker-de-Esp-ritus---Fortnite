from itertools import groupby
import io
import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as str_lit

IMG_FOLDER = "imagenes"
IMAGEN_FONDO_EXPORT_PATH = os.path.join(IMG_FOLDER, "fondo_catalogo.png")
IMAGEN_FONDO_APP_PATH = os.path.join(IMG_FOLDER, "fondo_app.png")
CHECK_ICON_PATH = os.path.join(IMG_FOLDER, "check_verde.png")
CORONA_ICON_PATH = os.path.join(IMG_FOLDER, "corona.png")

MAPA_NOMBRES = {
    "11-PUNTO_CERO-01_Punto-Cero_Normal": "Punto Cero",
    "11-PUNTO_CERO-02_Punto-Cero_Dorado": "Punto Cero Dorado",
    "11-PUNTO_CERO-03_Punto-Cero_Golosina": "Punto Cero Golosina",
    "11-PUNTO_CERO-04_Punto-Cero_Galáctico": "Punto Cero Galáctico",
    "11-PUNTO_CERO-05_Punto-Cero_Holo": "Punto Cero Holo",
    "11-PUNTO_CERO-06_Punto-Cero_Cubo": "Punto Cero Cubo",
    "11-PUNTO_CERO-07_Punto-Cero_Patito": "Punto Cero Patito",
    "11-PUNTO_CERO-08_Punto-Cero_Gema": "Punto Cero Gema",
    "12-PALITO_DE_PEZ-01_Palito-De_Pez_Normal": "Palito De Pez",
    "12-PALITO_DE_PEZ-02_Palito-De_Pez_Dorado": "Palito De Pez Dorado",
    "12-PALITO_DE_PEZ-03_Palito-De_Pez_Golosina": "Palito De Pez Golosina",
    "12-PALITO_DE_PEZ-04_Palito-De_Pez_Galáctico": "Palito De Pez Galáctico",
    "12-PALITO_DE_PEZ-05_Palito-De_Pez_Cubo": "Palito De Pez Cubo",
    "18-LOS_SIETE-01_Los_Siete_Normal": "Los Siete",
    "18-LOS_SIETE-02_Los_Siete_Dorado": "Los Siete Dorado",
    "18-LOS_SIETE-03_Los_Siete_Golosina": "Los Siete Golosina",
    "18-LOS_SIETE-04_Los_Siete_Galáctico": "Los Siete Galáctico",
    "18-LOS_SIETE-05_Los_Siete_Holo": "Los Siete Holo",
    "20-VINI_JR-01_Vini_Jr_Normal": "Vini Jr",
    "22-JOHN_WICK-01_John_Wick_Normal": "John Wick",
}

str_lit.set_page_config(
    page_title="Tracker de Espíritus", page_icon="✨", layout="wide"
)

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
    </style>
    """
  str_lit.markdown(custom_css, unsafe_allow_html=True)

if "seleccionados" not in str_lit.session_state:
  str_lit.session_state.seleccionados = set()

if "dominados" not in str_lit.session_state:
  str_lit.session_state.dominados = set()

if not os.path.exists(IMG_FOLDER):
  os.makedirs(IMG_FOLDER)


def obtener_titulo_categoria(nombre_archivo):
  partes = nombre_archivo.split("-")
  if len(partes) >= 2:
    return partes[1].replace("_", " ").title()
  return "General"


def obtener_variante(nombre_archivo):
  nombre_lower = nombre_archivo.lower()
  if "dorado" in nombre_lower:
    return "Dorado"
  elif "golosina" in nombre_lower:
    return "Golosina"
  elif "galáct" in nombre_lower or "galactic" in nombre_lower:
    return "Galáctico"
  elif "holo" in nombre_lower:
    return "Holográfico"
  elif "cubo" in nombre_lower or "cúbic" in nombre_lower:
    return "Cúbico"
  elif "patito" in nombre_lower:
    return "Patito"
  elif "gema" in nombre_lower:
    return "Gema"
  else:
    return "Normal"


def generar_imagen_coleccion(
    lista_ordenada_archivos,
    seleccionados,
    dominados,
    titulo_personalizado=None,
    usar_fondo_app=False,
    imagen_custom=None,
):
  columnas = 10
  ancho_celda = 90
  alto_celda = 110

  padding_lateral = 20
  padding_superior = 90

  filas = (len(lista_ordenada_archivos) // columnas) + 1

  ancho_total = (columnas * ancho_celda) + (padding_lateral * 2)
  alto_total = (filas * alto_celda) + padding_superior + 20

  ruta_fondo = (
      IMAGEN_FONDO_APP_PATH
      if usar_fondo_app and os.path.exists(IMAGEN_FONDO_APP_PATH)
      else IMAGEN_FONDO_EXPORT_PATH
  )

  if imagen_custom is not None:
    fondo_original = Image.open(imagen_custom).convert("RGBA")
    img_final = fondo_original.resize((ancho_total, alto_total))
  elif os.path.exists(ruta_fondo):
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
      fill=(15, 15, 15, 210),
  )

  for i in range(len(lista_ordenada_archivos)):
    x = padding_lateral + (i % columnas) * ancho_celda + 10
    y = padding_superior + (i // columnas) * alto_celda + 10

    nombre_base = os.path.splitext(lista_ordenada_archivos[i])[0]
    is_dom = nombre_base in dominados

    if is_dom:
      d_ui.rectangle(
          [x - 5, y - 5, x + 75, y + 100],
          fill=(255, 215, 0, 50),
          outline=(255, 215, 0, 200),
          width=2,
      )
    else:
      d_ui.rectangle([x - 5, y - 5, x + 75, y + 100], fill=(20, 20, 20, 140))

  img_final = Image.alpha_composite(img_final, capa_ui)

  ruta_fuente = os.path.join(IMG_FOLDER, "BURBANK.ttf")
  try:
    font_principal = ImageFont.truetype(ruta_fuente, 28)
    font_contador = ImageFont.truetype(ruta_fuente, 22)
  except IOError:
    font_principal = ImageFont.load_default()
    font_contador = ImageFont.load_default()

  d = ImageDraw.Draw(img_final)

  texto_titulo = (
      titulo_personalizado
      if titulo_personalizado
      else "MI COLECCIÓN DE ESPÍRITUS"
  )
  pos_x_titulo = padding_lateral + 15
  pos_y_titulo = 28

  for dx, dy in [
      (-2, 0),
      (2, 0),
      (0, -2),
      (0, 2),
      (-2, -2),
      (2, 2),
      (-2, 2),
      (2, -2),
  ]:
    d.text(
        (pos_x_titulo + dx, pos_y_titulo + dy),
        texto_titulo,
        fill=(0, 0, 0, 255),
        font=font_principal,
    )
  d.text(
      (pos_x_titulo, pos_y_titulo),
      texto_titulo,
      fill=(255, 255, 255, 255),
      font=font_principal,
  )

  total_items = len(lista_ordenada_archivos)
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

  img_check_mini = None
  if os.path.exists(CHECK_ICON_PATH):
    img_check_mini = (
        Image.open(CHECK_ICON_PATH).convert("RGBA").resize((22, 22))
    )

  img_corona_mini = None
  if os.path.exists(CORONA_ICON_PATH):
    img_corona_mini = (
        Image.open(CORONA_ICON_PATH).convert("RGBA").resize((24, 24))
    )

  current_x = pos_x_base
  if img_check_mini:
    img_final.paste(img_check_mini, (current_x, pos_y_iconos), img_check_mini)
    current_x += 26
  else:
    d.text((current_x, pos_y_texto), "✓", fill=(0, 255, 120), font=font_contador)
    current_x += 20

  texto_obt = f"{obtenidos_totales}/{total_items}"
  d.text(
      (current_x, pos_y_texto), texto_obt, fill=(255, 255, 255), font=font_contador
  )
  current_x += 70

  d.text(
      (current_x, pos_y_texto),
      "/",
      fill=(150, 150, 150),
      font=font_contador,
  )
  current_x += 20

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

  texto_dom = f"{dominados_totales}/{total_items}"
  d.text(
      (current_x, pos_y_texto), texto_dom, fill=(255, 255, 255), font=font_contador
  )

  img_check = None
  if os.path.exists(CHECK_ICON_PATH):
    img_check = Image.open(CHECK_ICON_PATH).convert("RGBA").resize((26, 26))

  img_corona = None
  if os.path.exists(CORONA_ICON_PATH):
    img_corona = Image.open(CORONA_ICON_PATH).convert("RGBA").resize((32, 32))

  for i, archivo in enumerate(lista_ordenada_archivos):
    ruta = os.path.join(IMG_FOLDER, archivo)
    img_espiritu = Image.open(ruta).convert("RGBA").resize((70, 70))

    x = padding_lateral + (i % columnas) * ancho_celda + 10
    y = padding_superior + (i // columnas) * alto_celda + 10

    img_final.paste(img_espiritu, (x, y), img_espiritu)

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
          [x + 22, y + 75, x + 48, y + 95], outline=(120, 120, 120), width=1
      )
      if img_check:
        img_final.paste(img_check, (x + 22, y + 73), img_check)
      else:
        d.text((x + 28, y + 76), "✓", fill=(0, 255, 120))

  buf = io.BytesIO()
  img_final.save(buf, format="PNG")
  return buf.getvalue()


if os.path.exists(IMG_FOLDER):
  archivos_crudos = sorted([
      f
      for f in os.listdir(IMG_FOLDER)
      if f.lower().endswith(".png")
      and not f.startswith("num_")
      and f
      not in [
          "fondo_catalogo.png",
          "fondo_app.png",
          "check_verde.png",
          "corona.png",
          "titulo_banner.png",
          "fuente_fallback.ttf",
      ]
  ])

  archivos_ordenados = list(archivos_crudos)
  todos_los_ids = [os.path.splitext(f)[0] for f in archivos_ordenados]

  categorias_disponibles = []
  for f in archivos_crudos:
    cat = obtener_titulo_categoria(f)
    if cat not in categorias_disponibles:
      categorias_disponibles.append(cat)

  orden_variantes_fijo = [
      "Normal",
      "Dorado",
      "Golosina",
      "Galáctico",
      "Holográfico",
      "Cúbico",
      "Patito",
      "Gema",
  ]
  variantes_disponibles = [
      v
      for v in orden_variantes_fijo
      if any(obtener_variante(f) == v for f in archivos_crudos)
  ]

  cat_to_ids = {}
  var_to_ids = {}

  for f in archivos_crudos:
    cat = obtener_titulo_categoria(f)
    var = obtener_variante(f)
    f_id = os.path.splitext(f)[0]

    if cat not in cat_to_ids:
      cat_to_ids[cat] = []
    cat_to_ids[cat].append(f_id)

    if var not in var_to_ids:
      var_to_ids[var] = []
    var_to_ids[var].append(f_id)

  # --- BARRA LATERAL ---
  with str_lit.sidebar:
    str_lit.header("⚙️ Opciones")
    filtro_vista = str_lit.radio(
        "Filtrar vista", ["Todos", "Pendientes", "Dominados"]
    )
    str_lit.markdown("---")

    is_all_checked = all(
        id_esp in str_lit.session_state.seleccionados for id_esp in todos_los_ids
    )
    is_all_dom = all(
        id_esp in str_lit.session_state.dominados for id_esp in todos_los_ids
    )


    def toggle_global_chk():
      current_all = all(
          id_esp in str_lit.session_state.seleccionados
          for id_esp in todos_los_ids
      )
      if current_all:
        str_lit.session_state.seleccionados.clear()
        str_lit.session_state.dominados.clear()
      else:
        for id_esp in todos_los_ids:
          str_lit.session_state.seleccionados.add(id_esp)


    str_lit.checkbox(
        "✅ Marcar Todos",
        value=is_all_checked,
        key="global_chk",
        on_change=toggle_global_chk,
    )


    def toggle_global_dom():
      current_all = all(
          id_esp in str_lit.session_state.dominados for id_esp in todos_los_ids
      )
      if current_all:
        str_lit.session_state.dominados.clear()
      else:
        for id_esp in todos_los_ids:
          str_lit.session_state.seleccionados.add(id_esp)
          str_lit.session_state.dominados.add(id_esp)


    str_lit.checkbox(
        "👑 Dominar Todos",
        value=is_all_dom,
        key="global_dom",
        on_change=toggle_global_dom,
    )
    str_lit.markdown("---")

    # --- MARCAR Y DOMINAR POR CATEGORÍA ---
    with str_lit.expander("📌 Marcar por categoría"):
      for cat in categorias_disponibles:
        ids_cat = cat_to_ids[cat]
        cat_checked_all = all(
            id_esp in str_lit.session_state.seleccionados for id_esp in ids_cat
        )

        def make_toggle_cat_chk(c_ids):
          def callback():
            curr_all = all(
                i in str_lit.session_state.seleccionados for i in c_ids
            )
            if curr_all:
              for i in c_ids:
                str_lit.session_state.seleccionados.discard(i)
                str_lit.session_state.dominados.discard(i)
            else:
              for i in c_ids:
                str_lit.session_state.seleccionados.add(i)

          return callback

        str_lit.checkbox(
            f"{cat}",
            value=cat_checked_all,
            key=f"exp_chk_{cat}",
            on_change=make_toggle_cat_chk(ids_cat),
        )

    with str_lit.expander("👑 Dominar por categoría"):
      for cat in categorias_disponibles:
        ids_cat = cat_to_ids[cat]
        cat_dom_all = all(
            id_esp in str_lit.session_state.dominados for id_esp in ids_cat
        )

        def make_toggle_cat_dom(c_ids):
          def callback():
            curr_all = all(i in str_lit.session_state.dominados for i in c_ids)
            if curr_all:
              for i in c_ids:
                str_lit.session_state.dominados.discard(i)
            else:
              for i in c_ids:
                str_lit.session_state.seleccionados.add(i)
                str_lit.session_state.dominados.add(i)

          return callback

        str_lit.checkbox(
            f"{cat}",
            value=cat_dom_all,
            key=f"exp_dom_{cat}",
            on_change=make_toggle_cat_dom(ids_cat),
        )

    # --- MARCAR Y DOMINAR POR VARIANTE (8 FIJAS) ---
    with str_lit.expander("📌 Marcar por variante"):
      for var in variantes_disponibles:
        ids_var = var_to_ids.get(var, [])
        if not ids_var:
          continue
        var_checked_all = all(
            i in str_lit.session_state.seleccionados for i in ids_var
        )

        def make_toggle_var_chk(v_ids):
          def callback():
            curr_all = all(
                i in str_lit.session_state.seleccionados for i in v_ids
            )
            if curr_all:
              for i in v_ids:
                str_lit.session_state.seleccionados.discard(i)
                str_lit.session_state.dominados.discard(i)
            else:
              for i in v_ids:
                str_lit.session_state.seleccionados.add(i)

          return callback

        str_lit.checkbox(
            f"{var}",
            value=var_checked_all,
            key=f"var_chk_{var}",
            on_change=make_toggle_var_chk(ids_var),
        )

    with str_lit.expander("👑 Dominar por variante"):
      for var in variantes_disponibles:
        ids_var = var_to_ids.get(var, [])
        if not ids_var:
          continue
        var_dom_all = all(i in str_lit.session_state.dominados for i in ids_var)

        def make_toggle_var_dom(v_ids):
          def callback():
            curr_all = all(i in str_lit.session_state.dominados for i in v_ids)
            if curr_all:
              for i in v_ids:
                str_lit.session_state.dominados.discard(i)
            else:
              for i in v_ids:
                str_lit.session_state.seleccionados.add(i)
                str_lit.session_state.dominados.add(i)

          return callback

        str_lit.checkbox(
            f"{var}",
            value=var_dom_all,
            key=f"var_dom_{var}",
            on_change=make_toggle_var_dom(ids_var),
        )

    str_lit.markdown("---")
    str_lit.info("Marca tus progresos y genera tu tarjeta abajo.")

  # --- CONTENIDO PRINCIPAL ---
  str_lit.title("✨ Tracker de Espíritus - Fortnite")
  str_lit.markdown(
      "Lleva el control de tus espíritus obtenidos y dominados, y genera tu"
      " tarjeta personalizada."
  )

  total_espiritus = len(todos_los_ids)
  obtenidos_count = len(str_lit.session_state.seleccionados)
  dominados_count = len(str_lit.session_state.dominados)

  col_m1, col_m2, col_m3 = str_lit.columns(3)
  with col_m1:
    str_lit.metric(label="Total Registrados", value=total_espiritus)
  with col_m2:
    str_lit.metric(label="Obtenidos", value=obtenidos_count)
  with col_m3:
    porcentaje_dominados = (
        (dominados_count / total_espiritus) * 100 if total_espiritus > 0 else 0
    )
    str_lit.metric(
        label=f"Dominados ({porcentaje_dominados:.1f}%)", value=dominados_count
    )

  str_lit.markdown("---")

  # --- FILTROS Y BUSCADOR ---
  col_busqueda, col_cat = str_lit.columns([2, 2])
  with col_busqueda:
    busqueda_texto = str_lit.text_input(
        "🔍 Buscar espíritu por nombre",
        value="",
        placeholder="Escribe el nombre del espíritu...",
    )
  with col_cat:
    opciones_menu_cat = ["Todos"] + categorias_disponibles
    categoria_seleccionada = str_lit.selectbox(
        "🎯 Filtrar por categoría",
        opciones_menu_cat,
        label_visibility="visible",
    )

  str_lit.subheader("📋 Lista de Colección (Agrupada por Categoría)")

  for categoria, grupo in groupby(
      archivos_ordenados, key=obtener_titulo_categoria
  ):
    if (
        categoria_seleccionada != "Todos"
        and categoria != categoria_seleccionada
    ):
      continue

    lista_grupo = list(grupo)

    grupo_filtrado = []
    for archivo in lista_grupo:
      nombre_base = os.path.splitext(archivo)[0]
      is_dom = nombre_base in str_lit.session_state.dominados

      if filtro_vista == "Pendientes" and is_dom:
        continue
      if filtro_vista == "Dominados" and not is_dom:
        continue

      nombre_crudo = MAPA_NOMBRES.get(
          nombre_base,
          nombre_base.split("_", 1)[-1]
          .replace("-", " ")
          .replace("_", " ")
          .title(),
      )
      nombre_mostrado = nombre_crudo.replace("Normal", "").strip()

      if (
          busqueda_texto
          and busqueda_texto.lower() not in nombre_mostrado.lower()
          and busqueda_texto.lower() not in nombre_base.lower()
      ):
        continue

      grupo_filtrado.append(archivo)

    if not grupo_filtrado:
      continue

    str_lit.markdown(f"### Categoría: {categoria}")
    cols = str_lit.columns(5)

    for i, archivo in enumerate(grupo_filtrado):
      nombre_base = os.path.splitext(archivo)[0]

      nombre_crudo = MAPA_NOMBRES.get(
          nombre_base,
          nombre_base.split("_", 1)[-1]
          .replace("-", " ")
          .replace("_", " ")
          .title(),
      )
      nombre_mostrado = nombre_crudo.replace("Normal", "").strip()
      variante_actual = obtener_variante(archivo)

      with cols[i % 5]:
        str_lit.image(f"{IMG_FOLDER}/{archivo}", width=100)
        str_lit.markdown(
            f"<div style='text-align: center; font-weight: bold; font-size:"
            f" 13px; margin-bottom: 2px;'>{nombre_mostrado}</div>"
            f"<div style='text-align: center; color: #aaa; font-size:"
            f" 11px; margin-bottom: 5px;'>({variante_actual})</div>",
            unsafe_allow_html=True,
        )

        is_checked = nombre_base in str_lit.session_state.seleccionados
        is_dom = nombre_base in str_lit.session_state.dominados

        c_btn1, c_btn2 = str_lit.columns(2)

        with c_btn1:
          etiqueta_chk = "✅" if is_checked else "⬜"
          if str_lit.button(
              etiqueta_chk, key=f"chk_{nombre_base}", use_container_width=True
          ):
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
            if str_lit.button(
                etiqueta_dom, key=f"dom_{nombre_base}", use_container_width=True
            ):
              if is_dom:
                str_lit.session_state.dominados.remove(nombre_base)
              else:
                str_lit.session_state.dominados.add(nombre_base)
              str_lit.rerun()
          else:
            str_lit.button(
                "🔒", key=f"dom_{nombre_base}", disabled=True, use_container_width=True
            )

  str_lit.markdown("---")
  str_lit.subheader("🖼️ Generar Tarjetas de Colección")

  fondo_custom_usuario = str_lit.file_uploader(
      "🎨 (Opcional) Subir imagen de fondo personalizada para la tarjeta",
      type=["png", "jpg", "jpeg", "webp"],
      help=(
          "Resolución recomendada: 940 px de ancho por ~1200 px a 1500 px de"
          " alto (Proporción vertical o HD). Si no subes ninguna, se usará el"
          " fondo por defecto."
      ),
  )

  if archivos_ordenados:
    img_bytes = generar_imagen_coleccion(
        archivos_ordenados,
        str_lit.session_state.seleccionados,
        str_lit.session_state.dominados,
        usar_fondo_app=False,
        imagen_custom=fondo_custom_usuario,
    )
    str_lit.download_button(
        label="📥 Crear y Descargar Imagen de Colección (General)",
        data=img_bytes,
        file_name="catalogo_espiritus.png",
        mime="image/png",
    )
  else:
    str_lit.info("No hay espíritus disponibles para descargar.")

  str_lit.markdown("---")

  # --- DESCARGA MÚLTIPLE POR VARIANTES ---
  with str_lit.expander("📥 Descarga Múltiple por Variantes"):
    str_lit.markdown(
        "Selecciona las variantes que deseas incluir en tu tarjeta personalizada."
    )

    variantes_seleccionadas_multi = []
    for var in variantes_disponibles:
      if str_lit.checkbox(f"{var}", key=f"desc_multi_{var}"):
        variantes_seleccionadas_multi.append(var)

    if variantes_seleccionadas_multi:
      archivos_multi_filtrados = []
      for v in variantes_seleccionadas_multi:
        archivos_multi_filtrados.extend(
            [f for f in archivos_crudos if obtener_variante(f) == v]
        )

      nombres_vars_str = ", ".join(variantes_seleccionadas_multi)
      img_bytes_multi = generar_imagen_coleccion(
          archivos_multi_filtrados,
          str_lit.session_state.seleccionados,
          str_lit.session_state.dominados,
          titulo_personalizado=f"VARIANTES: {nombres_vars_str.upper()}",
          usar_fondo_app=True,
          imagen_custom=fondo_custom_usuario,
      )
      str_lit.download_button(
          label="📥 Descargar Tarjeta de Variantes Seleccionadas",
          data=img_bytes_multi,
          file_name="catalogo_variantes_seleccionadas.png",
          mime="image/png",
      )
    else:
      str_lit.info(
          "Selecciona al menos una variante en el menú de arriba para habilitar"
          " la descarga."
      )

  # --- DESCARGA MÚLTIPLE POR CATEGORÍAS (restaurada) ---
  with str_lit.expander("📥 Descarga Múltiple por Categorías"):
    str_lit.markdown(
        "Selecciona las categorías que deseas incluir en tu tarjeta personalizada."
    )

    categorias_seleccionadas_multi = []
    for cat in categorias_disponibles:
      if str_lit.checkbox(f"{cat}", key=f"desc_multi_cat_{cat}"):
        categorias_seleccionadas_multi.append(cat)

    if categorias_seleccionadas_multi:
      archivos_multi_cat_filtrados = []
      for c in categorias_seleccionadas_multi:
        archivos_multi_cat_filtrados.extend(
            [f for f in archivos_crudos if obtener_titulo_categoria(f) == c]
        )

      nombres_cats_str = ", ".join(categorias_seleccionadas_multi)
      img_bytes_multi_cat = generar_imagen_coleccion(
          archivos_multi_cat_filtrados,
          str_lit.session_state.seleccionados,
          str_lit.session_state.dominados,
          titulo_personalizado=f"CATEGORÍAS: {nombres_cats_str.upper()}",
          usar_fondo_app=True,
          imagen_custom=fondo_custom_usuario,
      )
      str_lit.download_button(
          label="📥 Descargar Tarjeta de Categorías Seleccionadas",
          data=img_bytes_multi_cat,
          file_name="catalogo_categorias_seleccionadas.png",
          mime="image/png",
      )
    else:
      str_lit.info(
          "Selecciona al menos una categoría en el menú de arriba para habilitar"
          " la descarga."
      )

  # --- DESCARGA DE ESPÍRITUS INDIVIDUALES ---
  with str_lit.expander("📥 Descarga de Espíritus Individuales (Libre)"):
    str_lit.markdown(
        "Selecciona espíritus específicos de cualquier categoría para generar"
        " tu tarjeta personalizada."
    )

    espiritus_individuales_seleccionados = []
    for cat in categorias_disponibles:
      str_lit.markdown(f"**Categoría: {cat}**")
      archivos_de_cat = [
          f for f in archivos_crudos if obtener_titulo_categoria(f) == cat
      ]
      for archivo in archivos_de_cat:
        nombre_base = os.path.splitext(archivo)[0]
        nombre_crudo = MAPA_NOMBRES.get(
            nombre_base,
            nombre_base.split("_", 1)[-1]
            .replace("-", " ")
            .replace("_", " ")
            .title(),
        )
        nombre_mostrado = nombre_crudo.replace("Normal", "").strip()
        var_a = obtener_variante(archivo)

        if str_lit.checkbox(
            f"{nombre_mostrado} ({var_a})", key=f"indiv_down_{nombre_base}"
        ):
          espiritus_individuales_seleccionados.append(archivo)

    if espiritus_individuales_seleccionados:
      img_bytes_indiv = generar_imagen_coleccion(
          espiritus_individuales_seleccionados,
          str_lit.session_state.seleccionados,
          str_lit.session_state.dominados,
          titulo_personalizado="SELECCIÓN PERSONALIZADA",
          usar_fondo_app=True,
          imagen_custom=fondo_custom_usuario,
      )
      str_lit.download_button(
          label="📥 Descargar Tarjeta de Espíritus Seleccionados",
          data=img_bytes_indiv,
          file_name="catalogo_personalizado.png",
          mime="image/png",
      )
    else:
      str_lit.info("Selecciona al menos un espíritu para generar la tarjeta.")

else:
  str_lit.warning("Aún no he encontrado la carpeta de imágenes.")
