import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- Configurações gerais ---

st.set_page_config(
    page_title="Controle de Horímetro - Transjap",
    page_icon="🏭",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Paleta de cores sólida
PRIMARY_COLOR = "#0B3954"
SECONDARY_COLOR = "#BFD7EA"
BACKGROUND_COLOR = "#E0E0E0"
TEXT_COLOR = "#1B1B1B"

# CSS customizado
st.markdown(
    f"""
    <style>
        .css-1d391kg {{
            background-color: {BACKGROUND_COLOR};
        }}
        .css-18ni7ap {{
            color: {PRIMARY_COLOR};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .css-10trblm {{
            background-color: {SECONDARY_COLOR};
            padding: 1rem;
            border-radius: 8px;
        }}
        footer {{
            visibility: hidden;
        }}
        .stButton>button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 8px 18px;
        }}
        .stTextInput>div>input {{
            border-radius: 6px;
            border: 1.5px solid {PRIMARY_COLOR};
            padding: 6px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FOLDER = "dados"
DATA_FILE = os.path.join(DATA_FOLDER, "horimetro.csv")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# --- Funções ---

def carregar_dados():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["Data"])
    else:
        df = pd.DataFrame(
            columns=["Data", "Operador", "Frota", "Horímetro Inicial", "Horímetro Final", "Horas Trabalhadas"]
        )
        df.to_csv(DATA_FILE, index=False)
        return df

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

def calcular_horas(inicial, final):
    try:
        h = float(final) - float(inicial)
        return round(h, 2) if h >= 0 else 0
    except:
        return 0

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Horimetro')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

# --- Login simples ---

def login():
    st.session_state["logado"] = False
    st.title("Login - Controle de Horímetro")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "senha123":
            st.session_state["logado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

# --- App principal ---

st.title("Controle de Horímetro - Transjap")

df = carregar_dados()

# Sidebar menu
menu = st.sidebar.selectbox("Menu", ["Registrar Horímetro", "Visualizar Registros", "Exportar Dados"])

if menu == "Registrar Horímetro":
    st.subheader("Registrar novo horímetro")
    operador = st.text_input("Nome do Operador")
    frota = st.text_input("Número da Frota")
    horimetro_inicial = st.text_input("Horímetro Inicial")
    horimetro_final = st.text_input("Horímetro Final")
    data = st.date_input("Data")

    if st.button("Registrar"):
        if not operador or not frota or not horimetro_inicial or not horimetro_final:
            st.error("Por favor, preencha todos os campos.")
        else:
            horas_trabalhadas = calcular_horas(horimetro_inicial, horimetro_final)
            novo_registro = {
                "Data": pd.to_datetime(data),
                "Operador": operador,
                "Frota": frota,
                "Horímetro Inicial": float(horimetro_inicial),
                "Horímetro Final": float(horimetro_final),
                "Horas Trabalhadas": horas_trabalhadas,
            }
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            salvar_dados(df)
            st.success(f"Registro salvo com sucesso! Horas trabalhadas: {horas_trabalhadas} h")

elif menu == "Visualizar Registros":
    st.subheader("Registros de Horímetro")
    frota_filtrada = st.selectbox("Filtrar por frota", options=["Todas"] + sorted(df["Frota"].unique().tolist()))
    if frota_filtrada != "Todas":
        df_filtrado = df[df["Frota"] == frota_filtrada]
    else:
        df_filtrado = df.copy()

    if df_filtrado.empty:
        st.info("Nenhum registro encontrado.")
    else:
        st.dataframe(df_filtrado.sort_values(by="Data", ascending=False).reset_index(drop=True))
        st.markdown(f"**Total de registros:** {len(df_filtrado)}")
        st.markdown(f"**Total de horas registradas:** {round(df_filtrado['Horas Trabalhadas'].sum(), 2)} h")

elif menu == "Exportar Dados":
    st.subheader("Exportar dados para Excel")
    if df.empty:
        st.info("Nenhum dado para exportar.")
    else:
        excel_data = exportar_excel(df)
        st.download_button(
            label="Baixar arquivo Excel",
            data=excel_data,
            file_name="controle_horimetro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


