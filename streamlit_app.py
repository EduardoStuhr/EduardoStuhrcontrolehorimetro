import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Cria a pasta 'dados' se não existir (sem erro se já existir)
os.makedirs('dados', exist_ok=True)

# Caminho do arquivo CSV para armazenar os registros
caminho_csv = 'dados/horimetro_registros.csv'

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(caminho_csv):
        return pd.read_csv(caminho_csv)
    else:
        # Cria DataFrame vazio com as colunas esperadas
        colunas = ['Data', 'Operador', 'Frota', 'Horimetro Inicial', 'Horimetro Final', 'Horas Trabalhadas']
        return pd.DataFrame(columns=colunas)

# Função para salvar dados
def salvar_dados(df):
    df.to_csv(caminho_csv, index=False)

# App Streamlit
st.title('Controle de Horímetro - Máquinas Transjap')

# Formulário para registrar horímetro
with st.form('registro_form'):
    operador = st.text_input('Nome do operador')
    frota = st.selectbox('Número da frota', ['230', '231', '232', '233'])
    horimetro_inicial = st.number_input('Horímetro inicial', min_value=0.0, format="%.2f")
    horimetro_final = st.number_input('Horímetro final', min_value=0.0, format="%.2f")
    submitted = st.form_submit_button('Registrar')

    if submitted:
        if horimetro_final < horimetro_inicial:
            st.error('Horímetro final não pode ser menor que o inicial.')
        elif operador.strip() == '':
            st.error('Informe o nome do operador.')
        else:
            horas_trabalhadas = horimetro_final - horimetro_inicial
            data_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            novo_registro = {
                'Data': data_registro,
                'Operador': operador,
                'Frota': frota,
                'Horimetro Inicial': horimetro_inicial,
                'Horimetro Final': horimetro_final,
                'Horas Trabalhadas': round(horas_trabalhadas, 2)
            }

            df = carregar_dados()
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            salvar_dados(df)
            st.success('✅ Registro salvo com sucesso!')

# Exibir registros existentes
st.header('📊 Registros de Horímetro')

df = carregar_dados()

if not df.empty:
    frota_filtrada = st.selectbox('Filtrar por frota', options=['Todas'] + sorted(df['Frota'].unique().tolist()))
    if frota_filtrada != 'Todas':
        df_filtrado = df[df['Frota'] == frota_filtrada]
    else:
        df_filtrado = df

    st.dataframe(df_filtrado)

    st.markdown(f"**⏱️ Total de horas registradas:** {round(df_filtrado['Horas Trabalhadas'].sum(), 2)} h")
else:
    st.info('Nenhum registro encontrado.')

