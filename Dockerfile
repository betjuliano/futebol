# Dockerfile para rodar o Dashboard Futebol PRO com Streamlit

# Imagem base com Python
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . /app

# Instala as dependências
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
