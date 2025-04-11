# 📊 Dashboard Futebol PRO

Um dashboard interativo em Streamlit para análise preditiva de jogos de futebol com base em métricas como xG, probabilidades de placar, confiança estatística e modelos baseados em regras.

---

## 🚀 Como executar localmente

### Pré-requisitos
- Python 3.11+
- Git (opcional)

### Passo a passo

1. Clone este repositório ou baixe os arquivos:
```bash
git clone https://github.com/seuusuario/dashboard-futebol-pro.git
cd dashboard-futebol-pro
```

2. Crie um ambiente virtual e ative:
```bash
python -m venv env
source env/bin/activate      # Linux/macOS
env\Scripts\activate         # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o app:
```bash
streamlit run app.py
```

---

## 🐳 Rodando com Docker

```bash
docker build -t dashboard-futebol .
docker run -p 8501:8501 dashboard-futebol
```

---

## 📁 Estrutura do Projeto
```
├── app.py                  # Arquivo principal do Streamlit
├── jogos1004.xlsx          # Planilha de dados
├── requirements.txt
├── Dockerfile
├── modules/                # Código modularizado
│   ├── auth.py             # Autenticação por email
│   ├── data.py             # Lógica de carregamento e classificação
│   └── pages.py            # Interface e visualização
```

---

## 🔐 Autenticação
Usuários precisam digitar um email válido (pré-cadastrado) para acessar o dashboard. Você pode configurar os emails permitidos em `modules/auth.py`.

---

## ✨ Funcionalidades
- Classificação automática de modelos (Vitória Casa, BTTS, Alta Confiança etc.)
- Filtros dinâmicos e visuais
- Índice de confiança calculado automaticamente
- Visualização de gráficos, barras e linha do tempo dos jogos
- Suporte a Docker e Streamlit Cloud

---

## 📬 Contato
Desenvolvido por Juliano. Para sugestões ou melhorias, entre em contato!


#git add . && git commit -m "Atualização geral" && git push origin main

