import streamlit as st
import pandas as pd
import os

# Função para carregar dados do gado
def carregar_dados_gado():
    if os.path.exists("gado.csv"):
        return pd.read_csv("gado.csv")
    else:
        return pd.DataFrame(columns=["Chip", "Raca", "Data_Nascimento", "Peso", "Vacinas", "Observacoes"])

# Função para salvar dados do gado
def salvar_dados_gado(df):
    df.to_csv("gado.csv", index=False)

# Configuração da página
st.set_page_config(page_title="Controle de Gado", layout="wide")
st.title("🐄 Controle de Gado")

# Carregar dados do gado
df_gado = carregar_dados_gado()

# Formulário para adicionar novo animal
st.header("Adicionar Novo Animal")
with st.form("form_novo_animal"):
    col1, col2 = st.columns(2)
    with col1:
        chip = st.text_input("Número do Chip")
        raca = st.text_input("Raça")
        data_nascimento = st.date_input("Data de Nascimento")
    with col2:
        peso = st.number_input("Peso (kg)", min_value=0.0)
        vacinas = st.text_input("Vacinas Aplicadas")
        observacoes = st.text_area("Observações")
    if st.form_submit_button("Adicionar Animal"):
        novo_animal = {
            "Chip": chip,
            "Raca": raca,
            "Data_Nascimento": data_nascimento,
            "Peso": peso,
            "Vacinas": vacinas,
            "Observacoes": observacoes
        }
        df_gado = pd.concat([df_gado, pd.DataFrame([novo_animal])], ignore_index=True)
        salvar_dados_gado(df_gado)
        st.success("Animal adicionado com sucesso!")

# Lista de animais
st.header("📋 Lista de Animais")
if not df_gado.empty:
    for index, row in df_gado.iterrows():
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Chip:** {row['Chip']}")
            st.write(f"**Raça:** {row['Raca']}")
            st.write(f"**Data de Nascimento:** {row['Data_Nascimento']}")
        with col2:
            st.write(f"**Peso:** {row['Peso']} kg")
            st.write(f"**Vacinas:** {row['Vacinas']}")
            st.write(f"**Observações:** {row['Observacoes']}")
        
        if st.button(f"Excluir {row['Chip']}", key=f"excluir_{index}"):
            df_gado = df_gado.drop(index)
            salvar_dados_gado(df_gado)
            st.rerun()
        
        st.markdown("---")
else:
    st.write("Nenhum animal cadastrado ainda.")