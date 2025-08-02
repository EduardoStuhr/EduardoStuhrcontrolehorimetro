import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

os.makedirs('dados', exist_ok=True)
caminho_csv = 'dados/horimetro.csv'

def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Horimetro')
    return output.getvalue()

st.set_page_config(
    page_title="Controle de Horímetro",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Controle de Horímetro - Transjap")

# Carregar dados
if os.path.exists(caminho_csv):
    df = pd.read_csv(caminho_csv)
else:
    df = pd.DataFrame(columns=["Data", "Operador", "Frota", "Horimetro Inicial", "Horimetro Final", "Horas Trabalhadas"])

perfil = st.sidebar.selectbox("Perfil de acesso", options=["Operador", "Administrador"])

if perfil == "Operador":
    st.subheader("Registrar Horímetro")

    with st.form("form_horimetro"):
        operador = st.text_input("Nome do operador")
        frota = st.selectbox("Número da frota", sorted(df["Frota"].unique()) if not df.empty else ["230", "231", "232"])
        horimetro_inicial = st.number_input("Horímetro Inicial", min_value=0.0, format="%.2f")
        horimetro_final = st.number_input("Horímetro Final", min_value=0.0, format="%.2f")
        data_registro = st.date_input("Data do registro", datetime.today())
        enviar = st.form_submit_button("Registrar")

        if enviar:
            if horimetro_final < horimetro_inicial:
                st.error("Horímetro final não pode ser menor que inicial.")
            elif operador.strip() == "":
                st.error("Informe o nome do operador.")
            else:
                horas_trabalhadas = horimetro_final - horimetro_inicial
                novo_registro = {
                    "Data": data_registro.strftime("%Y-%m-%d"),
                    "Operador": operador,
                    "Frota": frota,
                    "Horimetro Inicial": horimetro_inicial,
                    "Horimetro Final": horimetro_final,
                    "Horas Trabalhadas": horas_trabalhadas
                }
                df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                df.to_csv(caminho_csv, index=False)
                st.success("✅ Registro salvo com sucesso!")

elif perfil == "Administrador":
    st.subheader("Painel Administrativo - Filtro por frota")

    if df.empty:
        st.info("Nenhum registro encontrado.")
    else:
        frotas_disponiveis = sorted(df["Frota"].unique())
        frota_filtrar = st.selectbox("Filtrar por frota", options=["Todas"] + frotas_disponiveis)

        if frota_filtrar != "Todas":
            df_filtrado = df[df["Frota"] == frota_filtrar]
        else:
            df_filtrado = df.copy()

        if df_filtrado.empty:
            st.info("Nenhum registro encontrado para esta frota.")
        else:
            st.dataframe(df_filtrado.sort_values(by="Data", ascending=False), use_container_width=True)

            total_horas = round(df_filtrado["Horas Trabalhadas"].sum(), 2)
            total_registros = df_filtrado.shape[0]
            st.markdown(f"**Total de registros:** {total_registros}")
            st.markdown(f"**Total de horas registradas:** {total_horas} h")

            excel_data = exportar_excel(df_filtrado)
            st.download_button(
                label="📥 Exportar registros para Excel",
                data=excel_data,
                file_name='registros_horimetro.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
