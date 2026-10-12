"""
StreamView Analytics - Dashboard para la Gerencia de Marketing (Dash + Plotly)

Este archivo solo LEE los 4 CSV que genera el notebook de preparación.
No limpia ni corrige datos: toda la limpieza se hizo en el notebook.

Archivos que debe tener en la misma carpeta:
    catalogo_limpio.csv, generos.csv, paises.csv, peliculas_finanzas.csv

Ejecución:
    pip install -r requirements.txt
    python app.py        ->  abrir http://127.0.0.1:8050
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

BASE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. CONSTANTES Y DICCIONARIOS DE PRESENTACIÓN (DARK THEME PREMIUM)
# ---------------------------------------------------------------------------
COL = {
    "morado": "#A855F7",        # Morado StreamView principal
    "morado_claro": "#C084FC",  # Morado acento brillante
    "morado_acento": "#D8B4FE", # Morado suave para textos/detalles
    "cian": "#06B6D4",          # Cian neón para contraste de Series
    "rosa": "#EC4899",          # Rosa neón para contraste alternativo
    "fondo": "#0D0D0D",         # Fondo general negro profundo
    "card": "#18181B",          # Fondo de tarjetas y filtros gris oscuro
    "borde": "#27272A",         # Bordes sutiles
    "borde_claro": "#3F3F46",   # Bordes destacados
    "texto": "#F9FAFB",         # Texto principal blanco suave
    "texto_sec": "#9CA3AF",     # Texto secundario gris claro
    "intro_bg": "#261A36",      # Fondo intro y avisos
    "intro_borde": "#7E22CE",   # Borde morado para intros y avisos
    # Compatibilidad con variables previas
    "azul": "#A855F7",
    "azul_claro": "#C084FC",
    "menta": "#06B6D4",
    "oscuro": "#F9FAFB",
    "acento": "#06B6D4",
    "gris": "#9CA3AF",
}

FORMATOS = {"Movie": "Películas", "TV Show": "Series"}
COL_FORMATO = {"Películas": COL["morado"], "Series": COL["cian"]}

MIN_VOTOS_TOP = 100      # el Top 10 exige al menos 100 votos
MIN_MONTO = 100_000      # base financiera: presupuesto e ingresos >= 100.000
MIN_TITULOS_GENERO = 30  # un género por formato necesita >= 30 títulos para graficarse
MIN_PELIS_GENERO = 15    # género con >= 15 películas para el retorno mediano

GEN_INVALIDOS = {"sin género", "unknown"}
PAIS_INVALIDOS = {"sin país"}
IDIOMA_INVALIDOS = {"sin idioma", "unknown", "xx", "und"}

GENEROS_ES = {
    "Drama": "Drama", "Comedy": "Comedia", "Animation": "Animación",
    "Thriller": "Suspenso", "Action": "Acción", "Crime": "Crimen",
    "Family": "Familia", "Mystery": "Misterio", "Romance": "Romance",
    "Horror": "Terror", "Action & Adventure": "Acción y aventura",
    "Sci-Fi & Fantasy": "Ciencia ficción y fantasía", "Documentary": "Documental",
    "Adventure": "Aventura", "Reality": "Reality", "Science Fiction": "Ciencia ficción",
    "Fantasy": "Fantasía", "Kids": "Infantil", "History": "Historia",
    "Talk": "Talk show", "Soap": "Telenovela", "TV Movie": "Película para TV",
    "Music": "Música", "War": "Bélico", "War & Politics": "Guerra y política",
    "Western": "Western", "News": "Noticias",
}
IDIOMAS_ES = {
    "en": "Inglés", "zh": "Chino", "ja": "Japonés", "ko": "Coreano", "es": "Español",
    "fr": "Francés", "de": "Alemán", "hi": "Hindi", "tl": "Tagalo", "pt": "Portugués",
    "ru": "Ruso", "it": "Italiano", "tr": "Turco", "ar": "Árabe", "nl": "Neerlandés",
    "cn": "Cantonés", "th": "Tailandés", "pl": "Polaco", "sv": "Sueco", "da": "Danés",
    "no": "Noruego", "id": "Indonesio", "cs": "Checo", "he": "Hebreo", "ta": "Tamil",
    "fi": "Finés", "el": "Griego", "hu": "Húngaro", "ro": "Rumano", "uk": "Ucraniano",
}
PAISES_ES = {
    "United States of America": "Estados Unidos", "United Kingdom": "Reino Unido",
    "Japan": "Japón", "China": "China", "South Korea": "Corea del Sur",
    "France": "Francia", "Canada": "Canadá", "Germany": "Alemania", "India": "India",
    "Spain": "España", "Belgium": "Bélgica", "Italy": "Italia", "Mexico": "México",
    "Brazil": "Brasil", "Australia": "Australia", "Hong Kong": "Hong Kong",
    "Turkey": "Turquía", "Russia": "Rusia", "Argentina": "Argentina",
    "Netherlands": "Países Bajos", "Sweden": "Suecia", "Denmark": "Dinamarca",
    "Thailand": "Tailandia", "Taiwan": "Taiwán", "Philippines": "Filipinas",
}


def gen_es(x):
    return GENEROS_ES.get(x, x)


def idioma_es(x):
    return IDIOMAS_ES.get(x, x)


def pais_es(x):
    return PAISES_ES.get(x, x)


# ---------------------------------------------------------------------------
# 2. CARGA DE DATOS (solo lectura)
# ---------------------------------------------------------------------------
def con_uid(tabla):
    """Identificador único de título: tipo + show_id (show_id se repite entre tipos)."""
    tabla["uid"] = tabla["type"].str[0] + tabla["show_id"].astype(str)
    tabla["formato"] = tabla["type"].map(FORMATOS)
    return tabla


def cargar():
    cat = pd.read_csv(BASE / "catalogo_limpio.csv", usecols=[
        "show_id", "type", "title", "release_year", "genres", "country", "language",
        "popularity", "vote_count", "valoracion", "budget", "revenue", "retorno",
        "budget_sospechoso"])
    gen = pd.read_csv(BASE / "generos.csv", usecols=[
        "show_id", "type", "género", "popularity", "valoracion", "release_year"])
    pais = pd.read_csv(BASE / "paises.csv", usecols=[
        "show_id", "type", "país", "popularity", "valoracion", "release_year"])
    cat, gen, pais = con_uid(cat), con_uid(gen), con_uid(pais)
    # Excluimos las etiquetas de ausencia de los rankings y filtros
    gen = gen[~gen["género"].str.casefold().isin(GEN_INVALIDOS)]
    pais = pais[~pais["país"].str.casefold().isin(PAIS_INVALIDOS)]
    cat["idioma_valido"] = ~cat["language"].astype(str).str.casefold().isin(IDIOMA_INVALIDOS)
    return cat, gen, pais


cat, gen_ok, pais_ok = cargar()
ANIO_MIN, ANIO_MAX = int(cat["release_year"].min()), int(cat["release_year"].max())
OPC_GENERO = [{"label": gen_es(g), "value": g}
              for g in sorted(gen_ok["género"].unique(), key=gen_es)]
OPC_PAIS = [{"label": pais_es(p), "value": p}
            for p in sorted(pais_ok["país"].unique(), key=pais_es)]

# Fechas en blanco puro para el RangeSlider
MARKS_ANIOS = {
    a: {"label": str(a), "style": {"color": "#FFFFFF", "fontSize": "11px", "fontWeight": "600"}}
    for a in range(ANIO_MIN, ANIO_MAX + 1, 3)
}
MARKS_ANIOS[ANIO_MAX] = {"label": str(ANIO_MAX), "style": {"color": "#FFFFFF", "fontSize": "11px", "fontWeight": "600"}}


def filtrar(formato, generos, paises, anios):
    """Aplica los 4 filtros al catálogo (una fila por título)."""
    desde, hasta = anios
    df = cat[cat["release_year"].between(desde, hasta)]
    if formato in FORMATOS:
        df = df[df["type"] == formato]
    if generos:
        df = df[df["uid"].isin(gen_ok.loc[gen_ok["género"].isin(generos), "uid"])]
    if paises:
        df = df[df["uid"].isin(pais_ok.loc[pais_ok["país"].isin(paises), "uid"])]
    return df


# ---------------------------------------------------------------------------
# 3. FORMATO Y COMPONENTES VISUALES
# ---------------------------------------------------------------------------
def num(x, d=1):
    """Número con formato chileno: miles con punto y decimales con coma."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "s/d"
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


CONFIG = {"displaylogo": False,
          "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d",
                                     "zoomIn2d", "zoomOut2d", "pan2d"],
          "toImageButtonOptions": {"format": "png", "scale": 2,
                                   "filename": "streamview_grafico"}}


def estilo(fig, alto=360, leyenda=True):
    fig.update_layout(
        height=alto,
        margin=dict(l=15, r=20, t=15, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#18181B",
        showlegend=leyenda,
        font=dict(family="Inter, system-ui, -apple-system, sans-serif", size=12, color="#E5E7EB"),
        legend=dict(
            orientation="h",
            y=1.14,
            x=0,
            title_text="",
            font=dict(color="#E5E7EB", size=11),
            bgcolor="rgba(0,0,0,0)"
        ),
        hoverlabel=dict(
            bgcolor="#18181B",
            bordercolor="#3F3F46",
            font=dict(color="#F9FAFB", family="Inter, system-ui, sans-serif")
        )
    )
    fig.update_xaxes(
        gridcolor="#27272A",
        zeroline=False,
        color="#9CA3AF",
        tickcolor="#27272A",
        linecolor="#27272A"
    )
    fig.update_yaxes(
        gridcolor="#27272A",
        zeroline=False,
        color="#9CA3AF",
        tickcolor="#27272A",
        linecolor="#27272A"
    )
    return fig


def tarjeta(titulo, subtitulo, fig):
    return html.Div([
        html.H3(titulo),
        html.P(subtitulo, className="chart-subtitle"),
        dcc.Graph(figure=fig, config=CONFIG)
    ], className="chart-card")


def kpi(etiqueta, valor, detalle=""):
    return html.Div([
        html.Div(etiqueta, className="kpi-label"),
        html.Div(valor, className="kpi-value"),
        html.Div(detalle, className="kpi-sub")
    ], className="kpi-card")


def intro(para, decide):
    return html.Div([
        html.Span([html.B("Para: "), html.Span(para)]),
        html.Span([html.B("Decide: "), html.Span(decide)])
    ], className="page-intro")


def aviso(texto):
    return html.Div(texto, className="aviso")


def mensajes(lista):
    return html.Div([
        html.H3("Mensajes clave"),
        html.Ul([html.Li(m) for m in lista])
    ], className="chart-card mensajes")


def grilla(*tarjetas, columnas=2):
    return html.Div(list(tarjetas), className=f"dashboard-grid cols-{columnas}")


# ---------------------------------------------------------------------------
# 4. VISTAS (una por pestaña)
# ---------------------------------------------------------------------------
def vista_resumen(df, formato):
    n = len(df)
    n_series = int((df["type"] == "TV Show").sum())
    val = df["valoracion"]
    idiomas = df[df["idioma_valido"]]
    lider = idiomas["language"].value_counts()
    paises = pais_ok.loc[pais_ok["uid"].isin(df["uid"]), "país"].nunique()

    kpis = html.Div([
        kpi("Títulos", num(n, 0), "en el filtro actual"),
        kpi("Series", f"{num(100 * n_series / n, 1)}%", f"{num(n_series, 0)} títulos"),
        kpi("Popularidad mediana", num(df["popularity"].median(), 1), "mitad del catálogo sobre este valor"),
        kpi("Valoración media", num(val.mean(), 2), f"{num(val.notna().sum(), 0)} títulos con votos"),
        kpi("Países", num(paises, 0), "con país informado"),
        kpi("Idiomas", num(idiomas["language"].nunique(), 0), "con idioma informado"),
        kpi("Idioma líder", idioma_es(lider.index[0]) if len(lider) else "s/d",
            f"{num(100 * lider.iloc[0] / len(idiomas), 1)}% de los títulos" if len(lider) else ""),
    ], className="kpi-grid")

    por = (df.groupby("formato").agg(cantidad=("uid", "size"),
                                      pop=("popularity", "median"),
                                      val=("valoracion", "mean"),
                                      votos=("valoracion", "count")).reset_index())
    msgs = []
    if len(por) == 2:
        s = por[por["formato"] == "Series"].iloc[0]
        p = por[por["formato"] == "Películas"].iloc[0]
        msgs.append(f"Las series tienen {num(s['pop'] / p['pop'], 1)} veces la popularidad mediana de las "
                    f"películas ({num(s['pop'], 1)} frente a {num(p['pop'], 1)}).")
        mejor, peor = (s, p) if s["val"] >= p["val"] else (p, s)
        msgs.append(f"Las {mejor['formato'].lower()} están mejor valoradas: {num(mejor['val'], 2)} frente a "
                    f"{num(peor['val'], 2)} (solo títulos con votos).")
    if len(lider):
        asia = idiomas["language"].isin(["zh", "ja", "ko"]).mean() * 100
        msgs.append(f"{idioma_es(lider.index[0])} concentra el {num(100 * lider.iloc[0] / len(idiomas), 1)}% "
                    f"de los títulos; chino, japonés y coreano suman {num(asia, 1)}%.")
    msgs.append("Los datos miden catálogo, popularidad y valoración; no miden retención ni comportamiento de usuarios.")

    fig_pop = px.bar(por, x="formato", y="pop", color="formato", color_discrete_map=COL_FORMATO)
    fig_pop.update_traces(
        text=[num(v, 1) for v in por["pop"]],
        textposition="outside",
        cliponaxis=False,
        textfont=dict(color="#F9FAFB", size=12)
    )
    fig_pop.update_layout(xaxis_title="", yaxis_title="Popularidad mediana")
    fig_pop.update_yaxes(range=[0, por["pop"].max() * 1.2])

    fig_val = px.bar(por, x="formato", y="val", color="formato", color_discrete_map=COL_FORMATO)
    fig_val.update_traces(
        text=[num(v, 2) for v in por["val"]],
        textposition="outside",
        cliponaxis=False,
        textfont=dict(color="#F9FAFB", size=12)
    )
    fig_val.update_layout(xaxis_title="", yaxis_title="Valoración media (0 a 10)")
    fig_val.update_yaxes(range=[0, 10])

    t1 = "Las series tienen mayor popularidad mediana que las películas" if len(por) == 2 else "Popularidad mediana del catálogo filtrado"
    t2 = "Valoración media por formato (solo títulos con votos)"
    return html.Div([
        intro("Directorio y Gerencia General", "dónde está el peso del catálogo y qué tan sólido es"),
        kpis,
        grilla(tarjeta(t1, "Mediana de popularidad por formato.", estilo(fig_pop, 320, False)),
               tarjeta(t2, "Promedio de vote_average en títulos con al menos un voto.", estilo(fig_val, 320, False))),
        mensajes(msgs),
    ])


def vista_catalogo(df, formato):
    uids = df["uid"]
    gen_f = gen_ok[gen_ok["uid"].isin(uids)]
    pais_f = pais_ok[pais_ok["uid"].isin(uids)]

    # Géneros: top 10 por cantidad, apilado por formato
    g = gen_f.groupby(["género", "formato"])["uid"].nunique().reset_index(name="cantidad")
    top_g = g.groupby("género")["cantidad"].sum().nlargest(10).index
    g = g[g["género"].isin(top_g)].copy()
    g["nombre"] = g["género"].map(gen_es)
    orden = g.groupby("nombre")["cantidad"].sum().sort_values().index.tolist()
    fig_g = px.bar(g, x="cantidad", y="nombre", color="formato", orientation="h",
                   color_discrete_map=COL_FORMATO, category_orders={"nombre": orden},
                   labels={"cantidad": "Títulos", "nombre": "", "formato": ""})
    tot = g.groupby("nombre")["cantidad"].sum().sort_values(ascending=False)
    t_g = (f"{tot.index[0]} y {tot.index[1]} lideran la oferta con {num(tot.iloc[0], 0)} y {num(tot.iloc[1], 0)} títulos"
           if len(tot) >= 2 else "Géneros con más títulos")

    # Países: top 12 por títulos
    p = pais_f.groupby("país").agg(cantidad=("uid", "nunique"),
                                   pop=("popularity", "median")).nlargest(12, "cantidad").reset_index()
    p["nombre"] = p["país"].map(pais_es)
    con_pais = pais_f["uid"].nunique()
    fig_p = px.bar(p.sort_values("cantidad"), x="cantidad", y="nombre", orientation="h",
                   labels={"cantidad": "Títulos", "nombre": ""}, hover_data={"pop": ":.1f"})
    fig_p.update_traces(marker_color=COL["morado"])
    t_p = (f"{p.iloc[0]['nombre']} lidera con {num(p.iloc[0]['cantidad'], 0)} títulos "
           f"({num(100 * p.iloc[0]['cantidad'] / con_pais, 1)}% de los que tienen país)") if len(p) else "Países con más títulos"

    # Idiomas: top 12 por títulos
    idi = df[df["idioma_valido"]].groupby("language").agg(cantidad=("uid", "size"),
                                                          pop=("popularity", "median")).nlargest(12, "cantidad").reset_index()
    idi["nombre"] = idi["language"].map(idioma_es)
    fig_i = px.bar(idi.sort_values("cantidad"), x="cantidad", y="nombre", orientation="h",
                   labels={"cantidad": "Títulos", "nombre": ""}, hover_data={"pop": ":.1f"})
    fig_i.update_traces(marker_color=COL["morado_claro"])
    total_idi = int(df["idioma_valido"].sum())
    t_i = (f"{idi.iloc[0]['nombre']} concentra el {num(100 * idi.iloc[0]['cantidad'] / total_idi, 1)}% de los títulos"
           if len(idi) else "Idiomas con más títulos")

    nota = aviso("Nota de catálogo: un título puede asociarse a múltiples géneros o países de coproducción, por lo que las sumas de categorías no equivalen directamente al total de títulos únicos.")
    return html.Div([
        intro("Equipo de Contenidos", "qué géneros, países e idiomas conviene adquirir o renovar"),
        grilla(tarjeta(t_g, "Top 10 géneros por cantidad de títulos, separados por formato.", estilo(fig_g, 400)),
               tarjeta(t_p, "Top 12 países por cantidad de títulos.", estilo(fig_p, 400, False))),
        grilla(tarjeta(t_i, "Top 12 idiomas por cantidad de títulos (idiomas informados).", estilo(fig_i, 400, False)),
               nota),
    ])


def vista_campanas(df, formato):
    # Top 10 títulos con al menos 100 votos
    top = df[df["vote_count"] >= MIN_VOTOS_TOP].nlargest(10, "popularity").sort_values("popularity")
    if len(top):
        n_s = int((top["type"] == "TV Show").sum())
        fig_t = px.bar(top, x="popularity", y="title", color="formato", orientation="h",
                       color_discrete_map=COL_FORMATO,
                       labels={"popularity": "Popularidad", "title": "", "formato": ""},
                       hover_data={"release_year": True, "vote_count": True, "valoracion": ":.2f", "formato": False})
        t_t = f"{n_s} de los {len(top)} títulos más populares son series"
    else:
        fig_t, t_t = go.Figure(), "Sin títulos con 100 votos o más en este filtro"

    # Oportunidad: género x formato (cada género se compara dentro de su formato)
    gen_f = gen_ok[gen_ok["uid"].isin(df["uid"])]
    g = gen_f.groupby(["género", "formato"]).agg(cantidad=("uid", "nunique"),
                                                 pop=("popularity", "median")).reset_index()
    g = g[g["cantidad"] >= MIN_TITULOS_GENERO].copy()
    g["nombre"] = g["género"].map(gen_es)
    fig_o, t_o = go.Figure(), "Pocos géneros con estos filtros para comparar oportunidades"
    if len(g) >= 4:
        p75, p35 = g["pop"].quantile(0.75), g["cantidad"].quantile(0.35)
        g["nicho"] = (g["pop"] > p75) & (g["cantidad"] < p35)
        g["etiqueta"] = np.where(g["pop"] > p75, g["nombre"], "")
        fig_o = px.scatter(g, x="cantidad", y="pop", color="formato", text="etiqueta",
                           color_discrete_map=COL_FORMATO, hover_name="nombre",
                           labels={"cantidad": "Cantidad de títulos (oferta)",
                                   "pop": "Popularidad mediana (demanda)", "formato": ""},
                           hover_data={"etiqueta": False})
        fig_o.update_traces(textposition="top center", textfont=dict(color="#F9FAFB", size=11),
                            marker=dict(size=13, opacity=0.85))
        fig_o.add_vline(x=p35, line_dash="dot", line_color=COL["morado_claro"])
        fig_o.add_hline(y=p75, line_dash="dot", line_color=COL["morado_claro"])
        nichos = g[g["nicho"]]
        if len(nichos):
            lista = ", ".join(f"{r.nombre} ({r.formato.lower()})" for r in nichos.itertuples())
            t_o = f"Oportunidad: {lista} combinan popularidad alta y oferta baja"
        else:
            t_o = "Con estos filtros ningún género combina popularidad alta y oferta baja"

    # Idiomas: popularidad mediana entre los 12 con más títulos
    idi = df[df["idioma_valido"]].groupby("language").agg(cantidad=("uid", "size"),
                                                          pop=("popularity", "median")).nlargest(12, "cantidad").reset_index()
    idi["nombre"] = idi["language"].map(idioma_es)
    if len(idi):
        mejor = idi.loc[idi["pop"].idxmax()]
        idi["color"] = np.where(idi["language"] == mejor["language"], "Mayor popularidad", "Resto")
        fig_i = px.bar(idi.sort_values("pop"), x="pop", y="nombre", orientation="h", color="color",
                       color_discrete_map={"Mayor popularidad": COL["cian"], "Resto": COL["morado"]},
                       labels={"pop": "Popularidad mediana", "nombre": "", "color": ""},
                       hover_data={"cantidad": True, "color": False})
        t_i = f"{mejor['nombre']} tiene la mayor popularidad mediana entre los 12 idiomas con más títulos"
    else:
        fig_i, t_i = go.Figure(), "Sin idiomas informados en este filtro"

    return html.Div([
        intro("Gerencia de Marketing", "qué títulos, géneros e idiomas promocionar y dónde probar campañas piloto"),
        grilla(tarjeta(t_t, "Top 10 por popularidad, solo títulos con 100 votos o más.", estilo(fig_t, 420)),
               tarjeta(t_o, f"Cada punto es un género dentro de su formato (mínimo {MIN_TITULOS_GENERO} títulos). "
                            "Líneas: percentil 75 de popularidad y percentil 35 de oferta. "
                            "Se comparan géneros dentro del mismo formato porque las series tienen mayor popularidad.",
                       estilo(fig_o, 420))),
        grilla(tarjeta(t_i, "Popularidad mediana de los 12 idiomas con más títulos.", estilo(fig_i, 380, False)),
               html.Div([
                   html.H3("Estrategia de Campañas"),
                   html.Ul([
                       html.Li([html.B("Campañas masivas: "), "priorizar los títulos con mayor tracción y volumen de votos del Top 10."]),
                       html.Li([html.B("Campañas continuas: "), "apoyarse en los géneros e idiomas con mayor volumen de oferta consolidada."]),
                       html.Li([html.B("Campañas de nicho: "), "activar títulos de géneros con alta demanda y baja oferta (alta oportunidad)."]),
                   ])
               ], className="chart-card mensajes")),
    ])


def vista_finanzas(df, formato):
    cabecera = intro("Directorio y equipo de Contenidos", "cuánto invertir en películas y qué tipo de película recupera mejor su presupuesto")
    if formato == "TV Show":
        return html.Div([cabecera, aviso("Los datos financieros existen solo para películas. Elige el formato "
                                          "'Todos' o 'Películas' para ver esta página.")])
    pelis = df[df["type"] == "Movie"]
    base = pelis[(pelis["budget"] >= MIN_MONTO) & (pelis["revenue"] >= MIN_MONTO) & (~pelis["budget_sospechoso"])]
    if len(pelis) == 0 or len(base) < 10:
        return html.Div([cabecera, aviso(f"Con estos filtros hay muy pocas películas con datos financieros "
                                          f"({num(len(base), 0)}). Amplía los filtros.")])

    recupera = (base["retorno"] >= 1).mean() * 100
    kpis = html.Div([
        kpi("Películas en el filtro", num(len(pelis), 0), ""),
        kpi("Con datos financieros", num(len(base), 0), f"{num(100 * len(base) / len(pelis), 1)}% de las películas"),
        kpi("Presupuesto mediano", num(base["budget"].median(), 0), "unidades de la fuente"),
        kpi("Ingresos medianos", num(base["revenue"].median(), 0), "unidades de la fuente"),
        kpi("Retorno mediano", f"{num(base['retorno'].median(), 2)}x", "ingresos / presupuesto"),
        kpi("Recuperan el presupuesto", f"{num(recupera, 1)}%", "retorno de 1x o más"),
    ], className="kpi-grid")

    # Retorno mediano por género
    gg = gen_ok[gen_ok["uid"].isin(base["uid"])].merge(base[["uid", "retorno"]], on="uid")
    r = gg.groupby("género").agg(n=("uid", "nunique"), mediana=("retorno", "median")).reset_index()
    r = r[r["n"] >= MIN_PELIS_GENERO].copy()
    r["nombre"] = r["género"].map(gen_es)
    if len(r) >= 2:
        r = r.sort_values("mediana")
        fig_r = px.bar(r, x="mediana", y="nombre", orientation="h",
                       labels={"mediana": "Retorno mediano (veces)", "nombre": ""}, hover_data={"n": True})
        fig_r.update_traces(marker_color=COL["morado"])
        fig_r.add_vline(x=1, line_dash="dot", line_color=COL["cian"], line_width=1.5)
        t_r = (f"{r.iloc[-1]['nombre']} tiene el mayor retorno mediano ({num(r.iloc[-1]['mediana'], 2)}x) "
               f"y {r.iloc[0]['nombre']} el menor ({num(r.iloc[0]['mediana'], 2)}x)")
    else:
        fig_r, t_r = go.Figure(), "Pocos géneros con películas suficientes para comparar"

    # Presupuesto vs ingresos
    sc = base.copy()
    sc["estado"] = np.where(sc["retorno"] >= 1, "Recupera el presupuesto", "No lo recupera")
    fig_s = px.scatter(sc, x="budget", y="revenue", color="estado", log_x=True, log_y=True, opacity=0.7,
                       color_discrete_map={"Recupera el presupuesto": COL["morado"], "No lo recupera": COL["rosa"]},
                       hover_name="title", hover_data={"release_year": True, "retorno": ":.2f", "estado": False},
                       labels={"budget": "Presupuesto (escala log)", "revenue": "Ingresos (escala log)", "estado": ""})
    lo, hi = min(sc["budget"].min(), sc["revenue"].min()), max(sc["budget"].max(), sc["revenue"].max())
    fig_s.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Ingresos = presupuesto",
                               line=dict(dash="dot", color=COL["texto_sec"], width=1.5), hoverinfo="skip"))
    t_s = f"{num(recupera, 0)}% de las películas con datos recupera su presupuesto"

    # Top 10 retorno
    top = base.nlargest(10, "retorno").sort_values("retorno")
    fig_t = px.bar(top, x="retorno", y="title", orientation="h",
                   labels={"retorno": "Retorno (veces)", "title": ""},
                   hover_data={"budget": ":,.0f", "revenue": ":,.0f", "release_year": True})
    fig_t.update_traces(marker_color=COL["morado_claro"])
    t_t = (f"Las 10 películas con mayor retorno tuvieron un presupuesto mediano de {num(top['budget'].median(), 0)}, "
           f"frente a {num(base['budget'].median(), 0)} del conjunto")

    return html.Div([
        cabecera, kpis,
        grilla(tarjeta(t_r, f"Películas con presupuesto e ingresos informados; géneros con al menos {MIN_PELIS_GENERO} películas. "
                            "La línea marca 1x (recupera lo invertido).", estilo(fig_r, 460, False)),
               tarjeta(t_s, "Cada punto es una película. Sobre la diagonal, los ingresos superan el presupuesto.",
                       estilo(fig_s, 460))),
        grilla(tarjeta(t_t, "Ranking de retorno (ingresos / presupuesto).", estilo(fig_t, 420, False)),
               aviso(f"Base financiera: películas con presupuesto e ingresos de al menos {num(MIN_MONTO, 0)} y presupuesto "
                     f"no sospechoso (n = {num(len(base), 0)}, {num(100 * len(base) / len(pelis), 1)}% de las películas del "
                     "filtro). Se descartan montos simbólicos que producen retornos irreales. El retorno es un múltiplo, no "
                     "una utilidad: no incluye marketing ni otros costos, y la fuente no documenta la moneda.")),
    ])


def vista_notas(df, formato):
    items_kpi = [
        ("Títulos", "cantidad de claves únicas (show_id, tipo)."),
        ("Popularidad mediana", "mediana de popularity; se usa mediana y no promedio por los valores extremos."),
        ("Valoración media", "promedio de vote_average solo en títulos con al menos un voto."),
        ("Países e idiomas", "cantidad de países e idiomas informados; se excluyen las etiquetas de ausencia."),
        ("Retorno", "ingresos / presupuesto, solo si ambos son positivos y no sospechosos."),
    ]
    limites = [
        "Los datos no permiten medir retención ni comportamiento de usuarios.",
        "Los datos financieros existen solo para películas, y solo un 22% tiene presupuesto e ingresos informados.",
        "La moneda de presupuesto e ingresos no está documentada.",
        "Los géneros dependen del formato: algunos existen solo en series y otros solo en películas, y las series tienen mayor popularidad; por eso se comparan dentro de su formato.",
        "La distribución de títulos por año es uniforme (2.000 por año), por eso no se muestran tendencias temporales y el año se usa solo como filtro.",
        "Los programas diarios (talk shows) acumulan emisiones y lideran la popularidad; no son comparables con un estreno.",
    ]
    return html.Div([
        intro("Todos los usuarios", "cómo interpretar los indicadores y qué límites tienen los datos"),
        html.Div([html.H3("Definiciones"), html.Ul([html.Li([html.B(a + ": "), b]) for a, b in items_kpi])],
                 className="chart-card mensajes"),
        html.Div([html.H3("Limitaciones"), html.Ul([html.Li(x) for x in limites])], className="chart-card mensajes"),
        html.Div([html.H3("Cómo usar los filtros"),
                  html.Ul([html.Li("Los filtros de formato, género, país y años se aplican a todas las páginas."),
                           html.Li("Con los géneros y países se pueden elegir varios a la vez; vacío significa todos."),
                           html.Li("Cada gráfico se puede descargar como imagen con el ícono de cámara al pasar el mouse."),
                           html.Li("El botón 'Descargar datos' exporta en CSV los títulos del filtro actual.")])],
                 className="chart-card mensajes"),
    ])


VISTAS = {"resumen": vista_resumen, "catalogo": vista_catalogo, "campanas": vista_campanas,
          "finanzas": vista_finanzas, "notas": vista_notas}

# ---------------------------------------------------------------------------
# 5. LAYOUT
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "StreamView Analytics"
server = app.server  # para publicar con gunicorn

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Span("STREAMVIEW", className="brand-badge-tag"),
            ], className="brand-badge-wrapper"),
            html.Div([
                html.H1("STREAMVIEW ANALYTICS", className="brand-title"),
                html.P("Panel de catálogo para decisiones de contenido y marketing", className="subtitle")
            ], className="brand-text-container"),
        ], className="brand-header-left"),
        html.Div(id="resumen-filtro", className="resumen-filtro"),
    ], className="header"),
    html.Div([
        html.Div([html.Label("Formato", className="filter-label"),
                  dcc.Dropdown(id="f-formato", clearable=False, searchable=False, value="Todos",
                               className="custom-dropdown",
                               options=[{"label": "Todos", "value": "Todos"},
                                        {"label": "Películas", "value": "Movie"},
                                        {"label": "Series", "value": "TV Show"}])],
                 className="filter-block"),
        html.Div([html.Label("Género", className="filter-label"),
                  dcc.Dropdown(id="f-genero", multi=True, options=OPC_GENERO, value=[],
                               className="custom-dropdown",
                               placeholder="Todos los géneros")], className="filter-block wide"),
        html.Div([html.Label("País", className="filter-label"),
                  dcc.Dropdown(id="f-pais", multi=True, options=OPC_PAIS, value=[],
                               className="custom-dropdown",
                               placeholder="Todos los países")], className="filter-block wide"),
        html.Div([html.Label("Años de estreno", className="filter-label"),
                  dcc.RangeSlider(id="f-anios", min=ANIO_MIN, max=ANIO_MAX, step=1,
                                  value=[ANIO_MIN, ANIO_MAX], allowCross=False,
                                  marks=MARKS_ANIOS,
                                  tooltip={"placement": "bottom"})], className="filter-block slider"),
        html.Div([html.Button("Limpiar filtros", id="btn-reset", className="btn"),
                  html.Button("Descargar datos", id="btn-csv", className="btn btn-primario"),
                  dcc.Download(id="descarga")], className="filter-block botones"),
    ], className="filtros"),
    dcc.Tabs(id="tabs", value="resumen", className="tabs", children=[
        dcc.Tab(label="Resumen ejecutivo", value="resumen", className="nav-tab", selected_className="nav-tab--selected"),
        dcc.Tab(label="Catálogo", value="catalogo", className="nav-tab", selected_className="nav-tab--selected"),
        dcc.Tab(label="Campañas", value="campanas", className="nav-tab", selected_className="nav-tab--selected"),
        dcc.Tab(label="Finanzas (películas)", value="finanzas", className="nav-tab", selected_className="nav-tab--selected"),
        dcc.Tab(label="Notas y definiciones", value="notas", className="nav-tab", selected_className="nav-tab--selected"),
    ]),
    html.Div(id="contenido"),
    html.Div("Fuente: catálogo StreamView (31.991 títulos, 2010 a 2025). Elaboración propia.", className="pie"),
], className="page")


# ---------------------------------------------------------------------------
# 6. CALLBACKS
# ---------------------------------------------------------------------------
@app.callback(Output("contenido", "children"), Output("resumen-filtro", "children"),
              Input("tabs", "value"), Input("f-formato", "value"), Input("f-genero", "value"),
              Input("f-pais", "value"), Input("f-anios", "value"))
def actualizar(tab, formato, generos, paises, anios):
    df = filtrar(formato, generos or [], paises or [], anios)
    texto = f"{num(len(df), 0)} de {num(len(cat), 0)} títulos con los filtros actuales"
    if df.empty:
        return aviso("No hay títulos con esta combinación de filtros. Prueba con menos filtros."), texto
    return VISTAS[tab](df, formato), texto


@app.callback(Output("f-formato", "value"), Output("f-genero", "value"),
              Output("f-pais", "value"), Output("f-anios", "value"),
              Input("btn-reset", "n_clicks"), prevent_initial_call=True)
def limpiar(_):
    return "Todos", [], [], [ANIO_MIN, ANIO_MAX]


@app.callback(Output("descarga", "data"), Input("btn-csv", "n_clicks"),
              State("f-formato", "value"), State("f-genero", "value"),
              State("f-pais", "value"), State("f-anios", "value"), prevent_initial_call=True)
def descargar(_, formato, generos, paises, anios):
    df = filtrar(formato, generos or [], paises or [], anios)
    salida = df[["title", "formato", "release_year", "genres", "country", "language", "popularity",
                 "vote_count", "valoracion", "budget", "revenue", "retorno"]]
    return dcc.send_data_frame(salida.to_csv, "streamview_filtrado.csv", index=False)


# ---------------------------------------------------------------------------
# 7. ESTILOS EMBEBIDOS (DARK THEME PREMIUM - STREAMING PLATFORM)
# ---------------------------------------------------------------------------
app.index_string = """
<!DOCTYPE html>
<html lang="es">
<head>
    {%metas%}
    <title>StreamView Analytics</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    {%favicon%}
    {%css%}
    <style>
        /* ================= BASE / RESET ================= */
        * { box-sizing: border-box; }
        body {
            margin: 0;
            background-color: #0D0D0D;
            color: #F9FAFB;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        .page {
            max-width: 1540px;
            margin: auto;
            padding: 26px 30px 48px;
        }

        /* ================= VARIABLES GLOBALES DE DASH ================= */
        :root,
        body,
        .dash-dropdown,
        .dash-dropdown-content {
            --Dash-Fill-Inverse-Strong: #27272A !important;
            --Dash-Text-Strong: #F9FAFB !important;
            --Dash-Text-Weak: #C084FC !important;
            --Dash-Text-Disabled: #9CA3AF !important;
            --Dash-Stroke-Strong: #3F3F46 !important;
            --Dash-Fill-Disabled: #27272A !important;
            --Dash-Fill-Interactive-Strong: #A855F7 !important;
            --Dash-Fill-Interactive-Weak: #2E1A47 !important;
            --Dash-Shading-Strong: rgba(0, 0, 0, 0.8) !important;
            --Dash-Shading-Weak: rgba(0, 0, 0, 0.5) !important;
        }

        /* ================= SCROLLBARS ================= */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0D0D0D; }
        ::-webkit-scrollbar-thumb { background: #27272A; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #3F3F46; }

        /* ================= HEADER & BRAND ================= */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .brand-header-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .brand-badge-wrapper {
            display: flex;
            align-items: center;
        }
        .brand-badge-tag {
            background: linear-gradient(135deg, #7E22CE 0%, #A855F7 100%);
            color: #FFFFFF;
            font-weight: 800;
            font-size: 11px;
            letter-spacing: 1.2px;
            padding: 6px 10px;
            border-radius: 6px;
            border: 1px solid rgba(232, 121, 249, 0.4);
            box-shadow: 0 0 16px rgba(168, 85, 247, 0.45);
            display: inline-block;
        }
        .brand-text-container {
            display: flex;
            flex-direction: column;
        }
        .brand-title {
            margin: 0;
            font-family: 'Inter', system-ui, sans-serif;
            font-weight: 800;
            font-size: 28px;
            letter-spacing: -0.6px;
            background: linear-gradient(135deg, #A855F7 0%, #E879F9 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.15;
        }
        .subtitle {
            color: #9CA3AF;
            margin: 3px 0 0;
            font-size: 13.5px;
            font-weight: 400;
        }
        .resumen-filtro {
            color: #C084FC;
            background: rgba(168, 85, 247, 0.08);
            border: 1px solid rgba(168, 85, 247, 0.3);
            border-radius: 9999px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.1);
        }

        /* ================= FILTER CONTAINER ================= */
        .filtros {
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: flex-end;
            background: #18181B;
            border: 1px solid #27272A;
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        }
        .filter-block {
            min-width: 170px;
        }
        .filter-block.wide {
            min-width: 240px;
            flex: 1;
        }
        .filter-block.slider {
            min-width: 310px;
            flex: 1.25;
            padding-bottom: 6px;
        }
        .filter-block.botones {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .filter-label {
            display: block;
            color: #9CA3AF;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 6px;
        }

        /* ================= DASH DROPDOWN (RADIX UI / MODERN ENGINE) ================= */
        .dash-dropdown,
        button.dash-dropdown {
            background-color: #27272A !important;
            background: #27272A !important;
            border: 1px solid #3F3F46 !important;
            border-radius: 8px !important;
            color: #F9FAFB !important;
            min-height: 38px !important;
            outline: none !important;
            box-shadow: none !important;
        }
        .dash-dropdown:hover {
            border-color: #A855F7 !important;
        }
        .dash-dropdown:focus,
        .dash-dropdown:focus-visible,
        .dash-dropdown[data-state="open"] {
            border-color: #A855F7 !important;
            box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.4) !important;
        }
        .dash-dropdown-value {
            color: #F9FAFB !important;
            font-weight: 500 !important;
            font-size: 13.5px !important;
        }
        .dash-dropdown-placeholder {
            color: #9CA3AF !important;
            font-size: 13px !important;
        }
        .dash-dropdown-trigger-icon {
            color: #C084FC !important;
            fill: #C084FC !important;
        }
        .dash-dropdown-value-count {
            background: #2E1A47 !important;
            color: #E9D5FF !important;
            border: 1px solid #7E22CE !important;
            font-weight: 600 !important;
        }
        .dash-dropdown-content,
        div.dash-dropdown-content {
            background-color: #18181B !important;
            background: #18181B !important;
            border: 1px solid #3F3F46 !important;
            border-radius: 10px !important;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.8) !important;
            color: #F9FAFB !important;
            z-index: 9999 !important;
        }
        .dash-dropdown-search-container {
            background-color: #27272A !important;
            background: #27272A !important;
            border: 1px solid #7E22CE !important;
            border-radius: 6px !important;
            box-shadow: 0 0 8px rgba(168, 85, 247, 0.25) !important;
        }
        .dash-dropdown-search {
            color: #F9FAFB !important;
            background: transparent !important;
            font-size: 13px !important;
        }
        .dash-dropdown-search::placeholder {
            color: #9CA3AF !important;
        }
        .dash-dropdown-search-icon {
            color: #A855F7 !important;
        }
        .dash-dropdown-actions {
            background-color: #18181B !important;
            border-top: 1px solid #27272A !important;
            border-bottom: 1px solid #27272A !important;
            padding: 8px 12px !important;
        }
        .dash-dropdown-action-button {
            color: #C084FC !important;
            font-weight: 600 !important;
            font-size: 12px !important;
        }
        .dash-dropdown-action-button:hover {
            color: #FFFFFF !important;
            text-shadow: 0 0 8px rgba(168, 85, 247, 0.6) !important;
        }
        .dash-dropdown-options {
            background-color: #18181B !important;
        }
        .dash-dropdown-option {
            background-color: #18181B !important;
            color: #F9FAFB !important;
            box-shadow: 0 -1px 0 0 #27272A inset !important;
            cursor: pointer !important;
        }
        .dash-dropdown-option:hover,
        .dash-dropdown-option[data-highlighted] {
            background-color: #2E1A47 !important;
            color: #E879F9 !important;
        }
        .dash-dropdown-option span,
        .dash-dropdown-option label,
        .dash-dropdown-option div {
            color: #F9FAFB !important;
            font-size: 13px !important;
        }
        .dash-dropdown-option:hover span,
        .dash-dropdown-option:hover label {
            color: #E879F9 !important;
        }
        .dash-dropdown-option input[type="checkbox"] {
            accent-color: #A855F7 !important;
            width: 15px !important;
            height: 15px !important;
        }

        /* ================= RETROCOMPATIBILIDAD CON SELECT CLÁSICO ================= */
        .Select-control {
            background-color: #27272A !important;
            background: #27272A !important;
            border: 1px solid #3F3F46 !important;
            border-radius: 8px !important;
            color: #F9FAFB !important;
        }
        .Select-value,
        .Select-value-label,
        .Select--single > .Select-control .Select-value {
            color: #F9FAFB !important;
        }
        .Select-placeholder {
            color: #9CA3AF !important;
        }
        .Select-menu-outer {
            background-color: #18181B !important;
            border: 1px solid #3F3F46 !important;
        }
        .Select-option {
            background-color: #18181B !important;
            color: #F9FAFB !important;
        }
        .Select-option:hover {
            background-color: #2E1A47 !important;
            color: #E879F9 !important;
        }

        /* ================= RANGE SLIDER (AÑOS DE ESTRENO) ================= */
        .rc-slider-rail {
            background-color: #27272A !important;
            height: 6px !important;
        }
        .rc-slider-track {
            background: linear-gradient(90deg, #A855F7 0%, #C084FC 100%) !important;
            height: 6px !important;
        }
        .rc-slider-handle {
            border: 2px solid #A855F7 !important;
            background-color: #0D0D0D !important;
            box-shadow: 0 0 10px rgba(168, 85, 247, 0.6) !important;
        }
        .rc-slider-mark-text,
        .rc-slider-mark-text-active,
        span.rc-slider-mark-text {
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 11px !important;
        }

        /* ================= BUTTONS ================= */
        .btn {
            border: 1px solid #A855F7;
            background: transparent;
            color: #C084FC;
            border-radius: 8px;
            padding: 9px 16px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            font-family: inherit;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        .btn:hover {
            background: rgba(168, 85, 247, 0.14);
            color: #FFFFFF;
            border-color: #C084FC;
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.25);
            transform: translateY(-1px);
        }
        .btn:active {
            transform: translateY(0);
        }
        .btn-primario {
            background: linear-gradient(135deg, #9333EA 0%, #A855F7 100%);
            border: 1px solid #C084FC;
            color: #FFFFFF;
            box-shadow: 0 4px 14px rgba(168, 85, 247, 0.35);
        }
        .btn-primario:hover {
            background: linear-gradient(135deg, #A855F7 0%, #C084FC 100%);
            border-color: #E879F9;
            box-shadow: 0 6px 20px rgba(168, 85, 247, 0.55);
            color: #FFFFFF;
            transform: translateY(-1px);
        }

        /* ================= TABS ================= */
        .tabs, .tab-container {
            margin-bottom: 20px;
            border-bottom: 1px solid #27272A;
            display: flex;
            background: transparent;
        }
        .nav-tab, .tab {
            background-color: #18181B !important;
            color: #9CA3AF !important;
            border: none !important;
            border-top: 1px solid #27272A !important;
            border-left: 1px solid #27272A !important;
            border-right: 1px solid #27272A !important;
            border-top-left-radius: 8px !important;
            border-top-right-radius: 8px !important;
            border-bottom: 3px solid transparent !important;
            padding: 12px 22px !important;
            font-weight: 600 !important;
            font-size: 13.5px !important;
            cursor: pointer !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin-right: 4px !important;
        }
        .nav-tab:hover, .tab:hover {
            color: #F9FAFB !important;
            background-color: #221B2D !important;
        }
        .nav-tab--selected, .tab--selected {
            background-color: #221533 !important;
            color: #F9FAFB !important;
            border-bottom: 3px solid #A855F7 !important;
            font-weight: 700 !important;
            box-shadow: inset 0 -2px 12px rgba(168, 85, 247, 0.22) !important;
        }

        /* ================= INTRO & AVISO ================= */
        .page-intro {
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            color: #F9FAFB;
            font-size: 13px;
            background: #261A36;
            border: 1px solid #7E22CE;
            border-radius: 10px;
            padding: 11px 18px;
            margin-bottom: 18px;
            box-shadow: 0 4px 16px rgba(126, 34, 206, 0.15);
        }
        .page-intro b {
            color: #D8B4FE;
        }
        .aviso {
            background: #261A36;
            border: 1px solid #7E22CE;
            border-radius: 12px;
            padding: 16px 20px;
            font-size: 13px;
            line-height: 1.55;
            color: #F9FAFB;
            box-shadow: 0 4px 16px rgba(126, 34, 206, 0.15);
        }

        /* ================= KPI CARDS ================= */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }
        .kpi-card {
            background: #18181B;
            border: 1px solid #27272A;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .kpi-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #A855F7 0%, transparent 80%);
            opacity: 0.7;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: #3F3F46;
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.12);
        }
        .kpi-label {
            color: #9CA3AF;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .kpi-value {
            color: #A855F7;
            font-size: 27px;
            font-weight: 800;
            margin-top: 7px;
            letter-spacing: -0.5px;
            text-shadow: 0 0 24px rgba(168, 85, 247, 0.28);
        }
        .kpi-sub {
            color: #9CA3AF;
            font-size: 11px;
            margin-top: 4px;
            min-height: 15px;
            line-height: 1.35;
        }

        /* ================= CHART CARDS & GRIDS ================= */
        .dashboard-grid {
            display: grid;
            gap: 16px;
            margin-bottom: 18px;
        }
        .dashboard-grid.cols-2 {
            grid-template-columns: repeat(2, 1fr);
        }
        .chart-card {
            background: #18181B;
            border: 1px solid #27272A;
            border-radius: 14px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            padding: 18px 20px 10px;
            transition: border-color 0.2s ease;
        }
        .chart-card:hover {
            border-color: #3F3F46;
        }
        .chart-card h3 {
            margin: 0 0 4px;
            font-size: 16px;
            font-weight: 700;
            color: #F9FAFB;
            line-height: 1.35;
        }
        .chart-subtitle {
            color: #9CA3AF;
            margin: 0 0 10px;
            font-size: 12px;
            line-height: 1.4;
        }

        /* ================= MENSAJES CLAVE ================= */
        .mensajes {
            margin-bottom: 18px;
            padding: 18px 22px;
        }
        .mensajes h3 {
            color: #D8B4FE;
            margin-bottom: 10px;
        }
        .mensajes ul {
            margin: 8px 0 0;
            padding-left: 20px;
        }
        .mensajes li {
            margin: 8px 0;
            font-size: 13.5px;
            line-height: 1.5;
            color: #E5E7EB;
        }
        .mensajes li b {
            color: #C084FC;
        }

        /* ================= PIE DE PÁGINA ================= */
        .pie {
            color: #6B7280;
            font-size: 12px;
            margin-top: 18px;
            text-align: center;
            padding: 18px 0;
            border-top: 1px solid #1F1F23;
        }

        /* ================= RESPONSIVE ================= */
        @media (max-width: 1024px) {
            .dashboard-grid.cols-2 { grid-template-columns: 1fr; }
            .page { padding: 18px 18px 36px; }
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
