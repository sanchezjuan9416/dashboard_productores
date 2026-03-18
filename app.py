import streamlit as st
import pandas as pd
import json
import re
import plotly.express as px

st.set_page_config(page_title="CONVENIO ISA/IICA EN EL SECTOR ARROZ - RESULTADOS SECANO 2025", layout="wide")

# =========================
# HEADER CON LOGOS
# =========================

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.image("logo1.png", width=120)

with col2:
    st.markdown(
        "<h2 style='text-align: center;'>CONVENIO ISA/IICA EN EL SECTOR ARROZ - RESULTADOS SECANO 2025</h2>",
        unsafe_allow_html=True
    )

with col3:
    st.image("logo2.png", width=120)

st.markdown("---")

# =========================
# CARGAR DATOS DEL HTML
# =========================

@st.cache_data
def cargar_html():
    with open("Listado Productores General.html", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    match = re.search(r'DATAJSONARRAY":(\[.*?\])', contenido)
    
    if match:
        data_json = match.group(1)
        data = json.loads(data_json)
        df = pd.DataFrame(data)
        return df
    else:
        return pd.DataFrame()

df = cargar_html()

# =========================
# LIMPIEZA DE DATOS
# =========================

columnas = [
    "Nombre_del_Productor",
    "Apellidos_del_Productor",
    "Cedula_del_Productor",
    "Telefono_Celular",
    "Provincias"
]

df = df[columnas].dropna(subset=["Nombre_del_Productor"])

df.rename(columns={
    "Provincias": "Provincia",
    "Nombre_del_Productor": "Nombre",
    "Apellidos_del_Productor": "Apellido"
}, inplace=True)

# Normalizar nombres
df["Provincia"] = df["Provincia"].str.strip().str.title()

# Corrección manual (clave para mapa)
reemplazos = {
    "Panama": "Panamá",
    "Panama Oeste": "Panamá Oeste",
    "Bocas Del Toro": "Bocas del Toro",
    "Los Santos": "Los Santos",
    "Veraguas": "Veraguas",
    "Colon": "Colón",
    "Darien": "Darién"
}

df["Provincia"] = df["Provincia"].replace(reemplazos)

# =========================
# FILTRO
# =========================

st.sidebar.header("Filtros")

provincias = sorted(df["Provincia"].dropna().unique())
prov_sel = st.sidebar.selectbox("📍 Provincia", ["Todas"] + provincias)

if prov_sel != "Todas":
    df_filtrado = df[df["Provincia"] == prov_sel]
else:
    df_filtrado = df.copy()

# =========================
# KPIs
# =========================

col1, col2 = st.columns(2)

col1.metric("👨‍🌾 Total Productores", len(df_filtrado))
col2.metric("📍 Provincias", df_filtrado["Provincia"].nunique())

# =========================
# TABLA
# =========================

st.subheader("📋 Listado de Productores")
st.dataframe(df_filtrado, use_container_width=True)

# =========================
# GRÁFICO
# =========================

st.subheader("📊 Productores por Provincia")

conteo = df_filtrado["Provincia"].value_counts().reset_index()
conteo.columns = ["Provincia", "Cantidad"]

fig_bar = px.bar(
    conteo,
    x="Provincia",
    y="Cantidad",
    color="Provincia",
    text="Cantidad"
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# MAPA DE PANAMÁ
# =========================

st.subheader("🗺️ Mapa de Productores por Provincia")

with open("panama.json", "r", encoding="utf-8") as f:
    geojson = json.load(f)

mapa_df = df["Provincia"].value_counts().reset_index()
mapa_df.columns = ["Provincia", "Cantidad"]

fig_map = px.choropleth(
    mapa_df,
    geojson=geojson,
    locations="Provincia",
    featureidkey="properties.name",
    color="Cantidad",
    color_continuous_scale="YlOrRd",
)

fig_map.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig_map, use_container_width=True)