import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re  # Importação do módulo re

tag = st.selectbox("Selecione o serviço", ["estudantes", "servidores-docentes", "externo"])
generate = st.button("Pesquisar ...")
url = f"https://www.dac.unicamp.br/portal/servicos/catalogo/{tag}"

if generate:
    st.write(f"Pesquisando serviços de {url}")
    res = requests.get(url)
    contents = BeautifulSoup(res.text, 'html.parser')

    # Encontrar todos os títulos de serviço (h3 com classe element-invisible)
    service_titles = contents.find_all("h3", class_="topico")
    data = []

    # Iterar sobre os títulos dos serviços para extrair os links
    for title_tag in service_titles:
        link_tag = title_tag.find("a")
        if link_tag and "href" in link_tag.attrs:
            url_servico = link_tag["href"]
            nome_servico = link_tag.text.strip()
            #st.write(f"Pesquisando... {nome_servico}")

            try:
                # Acessar a página individual do serviço
                response_servico = requests.get(url_servico)
                response_servico.raise_for_status()
                soup_servico = BeautifulSoup(response_servico.text, "html.parser")

                # Encontrar o elemento <p> com a classe "datapublicacao"
                data_info_element = soup_servico.find("p", class_="datepublicacao")
                
                if not data_info_element: 
                    data_info_element = soup_servico.find("p", class_="datapublicacao")
                    

                data_publicacao = "Não encontrada"
                data_atualizacao = "Não encontrada"

                if data_info_element:
                    data_info_text = data_info_element.text.strip()

                    # Extrair a data de publicação usando regex
                    publicacao_match = re.search(r"Publicado:\s*(\d{2}/\d{2}/\d{4})", data_info_text)
                    if publicacao_match:
                        data_publicacao = publicacao_match.group(1)

                    # Extrair a data de atualização usando regex
                    atualizacao_match = re.search(r"Última atualização:\s*(\d{2}/\d{2}/\d{4})", data_info_text)
                    if atualizacao_match:
                        data_atualizacao = atualizacao_match.group(1)

                # Adicionar os dados à lista
                #st.write(f"Adicionando... nome: {nome_servico}, URL: {url_servico}, publicado em: {data_publicacao}, atualizado em: {data_atualizacao}")
                st.write(f"{nome_servico}, publicado em: {data_publicacao}, atualizado em: {data_atualizacao}")
                data.append({
                    "Serviço": nome_servico,
                    "URL": url_servico,
                    "Data de Publicação": data_publicacao,
                    "Data de Atualização": data_atualizacao
                })

            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao acessar a página do serviço {nome_servico} ({url_servico}): {e}")
            except AttributeError as e:
                st.error(f"Erro ao encontrar as datas na página do serviço {nome_servico} ({url_servico}): {e}")

    # Criar um DataFrame com os dados
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(data)

    # Configurar para mostrar todas as linhas (se necessário)
    pd.set_option('display.max_rows', None)

    # Salvar o DataFrame em um arquivo CSV com o nome da tag
    csv_filename = f"dados_servicos_{tag}_dac.csv"
    df.to_csv(csv_filename, index=False, encoding='cp1252')

    # Mostrar o DataFrame na interface
    st.dataframe(df)

    # Adicionar botão de download
    with open(csv_filename, 'rb') as f:
        st.download_button(
            label="Download CSV",
            data=f,
            file_name=csv_filename,
            mime="text/csv"
        )

    st.success(f"Os dados foram salvos no arquivo {csv_filename}")