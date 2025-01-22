import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from PIL import Image
from io import BytesIO
import os
import plotly.graph_objects as go  # Para criar gráficos profissionais

# Chave da API do OpenWeatherMap (substitua pela sua própria chave)
API_KEY = "e3a6729ad886ce16e51118467f080ed8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Configuração da página do Streamlit
st.set_page_config(page_title="Painel da Fazenda", layout="wide")
st.title("🌾 Painel da Fazenda")

# Entradas do usuário na barra lateral
st.sidebar.header("Configurações")
localizacao = st.sidebar.text_input("Digite a Localização da Fazenda", "Montes Altos, PT")
url_camera = st.sidebar.text_input("Digite o URL da Câmera JPG", "http://seu-ip-camera/image.jpg")

# Função para buscar dados meteorológicos
def buscar_dados_climaticos(cidade):
    try:
        # Clima atual
        parametros_atual = {"q": cidade, "appid": API_KEY, "units": "metric"}
        resposta_atual = requests.get(BASE_URL, params=parametros_atual).json()
        
        # Previsão do tempo
        parametros_previsao = {"q": cidade, "appid": API_KEY, "units": "metric"}
        resposta_previsao = requests.get(FORECAST_URL, params=parametros_previsao).json()
        
        return resposta_atual, resposta_previsao
    except Exception as e:
        st.error(f"Erro ao buscar dados climáticos: {e}")
        return None, None

# Exibir Clima Atual
st.header("🌤️ Clima Atual")
clima_atual, previsao_clima = buscar_dados_climaticos(localizacao)

if clima_atual:
    # Informações básicas do clima
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperatura", f"{clima_atual['main']['temp']}°C")
    with col2:
        st.metric("Umidade", f"{clima_atual['main']['humidity']}%")
    with col3:
        st.metric("Velocidade do Vento", f"{clima_atual['wind']['speed']} m/s")

    # Informações adicionais do clima
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Pressão", f"{clima_atual['main']['pressure']} hPa")
    with col5:
        visibilidade_km = clima_atual.get('visibility', 0) / 1000  # Converter metros para quilômetros
        st.metric("Visibilidade", f"{visibilidade_km:.1f} km")
    with col6:
        st.metric("Nebulosidade", f"{clima_atual['clouds']['all']}%")

    # Nascer e pôr do sol
    nascer_sol = datetime.fromtimestamp(clima_atual['sys']['sunrise']).strftime('%H:%M:%S')
    por_sol = datetime.fromtimestamp(clima_atual['sys']['sunset']).strftime('%H:%M:%S')
    col7, col8 = st.columns(2)
    with col7:
        st.metric("Nascer do Sol", nascer_sol)
    with col8:
        st.metric("Pôr do Sol", por_sol)

    # Chuva e neve (se disponível)
    if 'rain' in clima_atual:
        volume_chuva = clima_atual['rain'].get('1h', 0)  # Volume de chuva na última hora
        st.metric("Chuva (Última Hora)", f"{volume_chuva} mm")
    if 'snow' in clima_atual:
        volume_neve = clima_atual['snow'].get('1h', 0)  # Volume de neve na última hora
        st.metric("Neve (Última Hora)", f"{volume_neve} mm")

    # Exibir ícone do clima
    icone_clima = clima_atual['weather'][0]['icon']
    st.image(f"http://openweathermap.org/img/wn/{icone_clima}@2x.png", width=100)

# Exibir Previsão do Tempo (Compacta e Estilosa)
st.header("📅 Previsão do Tempo")
if previsao_clima:
    # Agrupar dados da previsão por dia
    previsao_por_dia = {}
    for previsao in previsao_clima['list']:
        data = previsao['dt_txt'].split()[0]  # Extrair a data (AAAA-MM-DD)
        if data not in previsao_por_dia:
            previsao_por_dia[data] = {
                "temperaturas": [],
                "clima": [],
                "icones": []
            }
        previsao_por_dia[data]["temperaturas"].append(previsao['main']['temp'])
        previsao_por_dia[data]["clima"].append(previsao['weather'][0]['description'])
        previsao_por_dia[data]["icones"].append(previsao['weather'][0]['icon'])

    # Exibir previsão em uma tabela compacta
    st.write("**Previsão Diária**")
    for data, dados in previsao_por_dia.items():
        temp_min = min(dados["temperaturas"])
        temp_max = max(dados["temperaturas"])
        clima_mais_comum = max(set(dados["clima"]), key=dados["clima"].count)  # Descrição mais frequente
        icone_mais_comum = max(set(dados["icones"]), key=dados["icones"].count)  # Ícone mais frequente

        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
        with col1:
            st.image(f"http://openweathermap.org/img/wn/{icone_mais_comum}@2x.png", width=50)
        with col2:
            st.write(f"**{data}**")
            st.write(f"{clima_mais_comum}")
        with col3:
            st.write(f"**Máx:** {temp_max}°C")
        with col4:
            st.write(f"**Mín:** {temp_min}°C")
        st.markdown("---")  # Adicionar uma linha horizontal para separação

# Criar um Gráfico Plotly para Dados Climáticos
st.header("📊 Tendências Climáticas")
if previsao_clima:
    # Extrair dados para o gráfico
    datas = []
    temperaturas = []
    umidade = []
    probabilidade_chuva = []
    volume_chuva_mm = []

    for previsao in previsao_clima['list']:
        datas.append(previsao['dt_txt'])
        temperaturas.append(previsao['main']['temp'])
        umidade.append(previsao['main']['humidity'])
        probabilidade_chuva.append(previsao.get('pop', 0) * 100)  # Probabilidade de precipitação (0-100%)
        volume_chuva_mm.append(previsao.get('rain', {}).get('3h', 0))  # Volume de chuva em mm (últimas 3 horas)

    # Criar uma figura Plotly
    fig = go.Figure()

    # Adicionar linha de temperatura
    fig.add_trace(go.Scatter(
        x=datas, y=temperaturas, mode='lines+markers', name='Temperatura (°C)',
        line=dict(color='red', width=2), marker=dict(size=8)
    ))

    # Adicionar linha de umidade
    fig.add_trace(go.Scatter(
        x=datas, y=umidade, mode='lines+markers', name='Umidade (%)',
        line=dict(color='blue', width=2), marker=dict(size=8)
    ))

    # Adicionar linha de probabilidade de chuva
    fig.add_trace(go.Scatter(
        x=datas, y=probabilidade_chuva, mode='lines+markers', name='Probabilidade de Chuva (%)',
        line=dict(color='green', width=2), marker=dict(size=8)
    ))

    # Adicionar linha de volume de chuva
    fig.add_trace(go.Scatter(
        x=datas, y=volume_chuva_mm, mode='lines+markers', name='Volume de Chuva (mm)',
        line=dict(color='purple', width=2), marker=dict(size=8)
    ))

    # Atualizar layout para um visual profissional
    fig.update_layout(
        title="Tendências Climáticas ao Longo do Tempo",
        xaxis_title="Data e Hora",
        yaxis_title="Valores",
        legend_title="Métricas",
        template="plotly_white",
        hovermode="x unified"
    )

    # Exibir o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Calendário com Eventos
st.header("📅 Calendário da Fazenda")

# Carregar eventos salvos do arquivo
try:
    with open("eventos_fazenda.txt", "r") as f:
        eventos_calendario = [linha.strip().split("|") for linha in f.readlines()]
except FileNotFoundError:
    eventos_calendario = []

# Adicionar evento ao calendário
data_evento = st.date_input("Selecione a Data")
nome_evento = st.text_input("Nome do Evento")
if st.button("Adicionar Evento"):
    eventos_calendario.append([str(data_evento), nome_evento])  # Armazenar como uma lista
    with open("eventos_fazenda.txt", "a") as f:
        f.write(f"{data_evento}|{nome_evento}\n")
    st.success(f"Evento '{nome_evento}' adicionado em {data_evento}")

# Exibir Calendário com Opção de Exclusão
if eventos_calendario:
    st.write("Próximos Eventos:")
    for i, evento in enumerate(eventos_calendario):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"- {evento[1]} em {evento[0]}")
        with col2:
            if st.button(f"Excluir {i+1}"):
                # Remover o evento da lista
                eventos_calendario.pop(i)
                # Reescrever o arquivo sem o evento excluído
                with open("eventos_fazenda.txt", "w") as f:
                    for ev in eventos_calendario:
                        f.write(f"{ev[0]}|{ev[1]}\n")
                st.rerun()  # Atualizar o app para refletir as mudanças

# Bloco de Notas
st.header("📝 Bloco de Notas")
nota = st.text_area("Escreva suas notas aqui")
if st.button("Salvar Nota"):
    with open("notas_fazenda.txt", "a") as f:
        f.write(f"{datetime.now()}: {nota}\n")
    st.success("Nota salva!")

# Exibir Notas Salvas com Opção de Exclusão
st.header("📖 Notas Salvas")
try:
    with open("notas_fazenda.txt", "r") as f:
        notas_salvas = f.readlines()
    if notas_salvas:
        for i, nota in enumerate(notas_salvas):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(nota)
            with col2:
                if st.button(f"Excluir {i+1}", key=f"nota_{i}"):
                    # Remover a nota da lista
                    notas_salvas.pop(i)
                    # Reescrever o arquivo sem a nota excluída
                    with open("notas_fazenda.txt", "w") as f:
                        for n in notas_salvas:
                            f.write(n)
                    st.rerun()  # Atualizar o app para refletir as mudanças
    else:
        st.write("Nenhuma nota salva ainda.")
except FileNotFoundError:
    st.write("Nenhuma nota salva ainda.")

# Calendário de Plantio
st.header("🌱 Calendário de Plantio")
dados_plantio = {
    "Cultura": ["Tomate", "Cenoura", "Batata", "Alface"],
    "Mês de Plantio": ["Março", "Abril", "Fevereiro", "Maio"],
    "Mês de Colheita": ["Agosto", "Julho", "Junho", "Setembro"]
}
df_plantio = pd.DataFrame(dados_plantio)
st.dataframe(df_plantio)

# Feed da Câmera (URL JPG)
st.header("📷 Feed da Câmera")
if url_camera:
    try:
        # Buscar a imagem do URL
        resposta = requests.get(url_camera)
        if resposta.status_code == 200:
            # Converter a imagem para um formato que o Streamlit pode exibir
            imagem = Image.open(BytesIO(resposta.content))
            st.image(imagem, caption="Última Imagem da Câmera", use_container_width=True)
        else:
            st.warning(f"Não foi possível buscar a imagem. Código de status: {resposta.status_code}")
    except Exception as e:
        st.error(f"Erro ao buscar imagem da câmera: {e}")
else:
    st.warning("Por favor, insira um URL válido para a câmera.")

# Notificações/Alertas
st.header("🔔 Notificações")
if st.button("Testar Notificação"):
    st.toast("Esta é uma notificação de teste!", icon="🔔")

# Atualizar automaticamente o app a cada 100 segundos
if st.button("Atualizar App"):
    st.rerun()

# Agendar atualização automática a cada 100 segundos
time.sleep(100)
st.rerun()

# Executar o app
if __name__ == "__main__":
    st.write("Bem-vindo ao Painel da Fazenda!")
