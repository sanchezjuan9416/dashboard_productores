import streamlit as st
import pandas as pd
import json
import re
import plotly.express as px
import base64

# =========================
# CONFIGURACIÓN
# =========================

st.set_page_config(
    page_title="ISA/IICA - Secano 2025",
    layout="wide"
)

# =========================
# ESTILOS
# =========================

st.markdown("""
    <style>
    .main {
        background-color: #F5F7FA;
    }
    h2 {
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    st.image("logo1.png", width=110)

with col2:
    st.markdown(
        "<h2 style='text-align: center; color:#2E7D32;'>CONVENIO ISA/IICA - RESULTADOS SECANO 2025</h2>",
        unsafe_allow_html=True
    )

with col3:
    st.image("logo2.png", width=110)

st.markdown("---")

# =========================
# CARGAR DATOS
# =========================

@st.cache_data
def cargar_html():
    with open("Listado Productores General.html", "r", encoding="utf-8") as f:
        contenido = f.read()
    
    match = re.search(r'DATAJSONARRAY":(\[.*?\])', contenido)
    
    if match:
        data_json = match.group(1)
        data = json.loads(data_json)
        return pd.DataFrame(data)
    return pd.DataFrame()

df = cargar_html()

# =========================
# LIMPIEZA
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

df["Provincia"] = df["Provincia"].str.strip().str.title()

df["Provincia"] = df["Provincia"].replace({
    "Panama": "Panamá",
    "Panama Oeste": "Panamá Oeste",
    "Colon": "Colón",
    "Darien": "Darién",
    "Bocas Del Toro": "Bocas del Toro"
})

# =========================
# FILTRO
# =========================

st.sidebar.header("🔎 Filtros")

provincias = sorted(df["Provincia"].dropna().unique())
prov_sel = st.sidebar.selectbox("📍 Provincia", ["Todas"] + provincias)

df_filtrado = df if prov_sel == "Todas" else df[df["Provincia"] == prov_sel]

# =========================
# KPIs
# =========================

col1, col2 = st.columns(2)

col1.metric("👨‍🌾 Productores", len(df_filtrado))
col2.metric("📍 Provincias", df_filtrado["Provincia"].nunique())

# =========================
# TABLA
# =========================

st.subheader("📋 Listado de Productores")
st.dataframe(df_filtrado, use_container_width=True)

# =========================
# GRÁFICO PRINCIPAL
# =========================

st.subheader("📊 Productores por Provincia")

conteo = df_filtrado["Provincia"].value_counts().reset_index()
conteo.columns = ["Provincia", "Cantidad"]

fig_bar = px.bar(
    conteo,
    x="Provincia",
    y="Cantidad",
    text="Cantidad",
    color="Cantidad",
    color_continuous_scale="Greens"
)

fig_bar.update_traces(
    texttemplate="<b>%{text}</b>",
    textposition="outside",
    textfont=dict(size=16)
)

fig_bar.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# RESULTADOS SECANO
# =========================

st.markdown("---")
st.header("📊 Resultados Secano 2025")

df_secano = pd.DataFrame({
    "Provincia": ["Chiriquí", "Coclé", "Darién", "Herrera", "Los Santos", "Panamá Este", "Veraguas"],
    "Asegurados": [6, 36, 5, 11, 24, 5, 8],
    "Registrados": [6, 31, 5, 7, 17, 7, 9]
})

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Asegurados", df_secano["Asegurados"].sum())
col2.metric("Registrados", df_secano["Registrados"].sum())
col3.metric("Cobertura (%)", round((df_secano["Registrados"].sum() / df_secano["Asegurados"].sum()) * 100, 2))

# Comparación
st.subheader("Asegurados vs Registrados")

fig1 = px.bar(
    df_secano,
    x="Provincia",
    y=["Asegurados", "Registrados"],
    barmode="group",
    color_discrete_sequence=["#2E7D32", "#1565C0"]
)

fig1.update_traces(
    texttemplate="<b>%{value}</b>",
    textposition="outside",
    textfont=dict(size=15)
)

fig1.update_layout(plot_bgcolor="white", paper_bgcolor="white")

st.plotly_chart(fig1, use_container_width=True)

# Hectáreas
st.subheader("🌱 Hectáreas")

df_hectareas = pd.DataFrame({
    "Provincia": ["Chiriquí", "Coclé", "Darién", "Herrera", "Los Santos", "Panamá", "Veraguas"],
    "Sembradas": [26088.8, 16654.7, 11079.7, 3633.6, 11286.9, 17935.9, 12251],
    "Registradas": [234, 1139, 100, 404, 65, 31, 200]
})

fig2 = px.bar(
    df_hectareas,
    x="Provincia",
    y=["Sembradas", "Registradas"],
    barmode="group",
    color_discrete_sequence=["#66BB6A", "#1E88E5"]
)

fig2.update_traces(
    texttemplate="<b>%{value}</b>",
    textposition="outside",
    textfont=dict(size=14)
)

fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")

st.plotly_chart(fig2, use_container_width=True)

# PIE CHARTS
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Tenencia de Finca")
    df_tenencia = pd.DataFrame({
        "Tipo": ["Propia", "Alquiler"],
        "Porcentaje": [73.17, 26.83]
    })
    fig3 = px.pie(
        df_tenencia,
        names="Tipo",
        values="Porcentaje",
        color_discrete_sequence=["#2E7D32", "#A5D6A7"]
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("👨‍🌾 Género")
    df_genero = pd.DataFrame({
        "Genero": ["Hombres", "Mujeres"],
        "Porcentaje": [78.04, 21.95]
    })
    fig4 = px.pie(
        df_genero,
        names="Genero",
        values="Porcentaje",
        color_discrete_sequence=["#1565C0", "#90CAF9"]
    )
    st.plotly_chart(fig4, use_container_width=True)

# Insumos
st.subheader("🧪 Uso de Insumos")

df_insumos = pd.DataFrame({
    "Indicador": ["Fertilizante", "Fungicidas", "Insecticidas", "Semilla"],
    "Valor": [8.5, 2.4, 3.8, 3.3]
})

fig5 = px.bar(
    df_insumos,
    x="Indicador",
    y="Valor",
    text="Valor",
    color="Valor",
    color_continuous_scale="Blues"
)

fig5.update_traces(
    texttemplate="<b>%{text}</b>",
    textposition="outside",
    textfont=dict(size=15)
)

fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white")

st.plotly_chart(fig5, use_container_width=True)

# =========================
# PDF
# =========================

st.subheader("📄 Informe Completo")

# BOTÓN DESCARGA
with open("resultados_secano_2025.pdf", "rb") as f:
    st.download_button(
        label="📥 Descargar PDF",
        data=f,
        file_name="resultados_secano_2025.pdf",
        mime="application/pdf"
    )
