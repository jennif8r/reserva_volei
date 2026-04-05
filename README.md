# 🏐 Vôlei Praça Osvaldo | Bot & Hub da Equipe

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://reserva-volei-osvaldo.streamlit.app/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated_Bot-2088FF?logo=github-actions)](https://github.com/)

> **O Fim da Confusão de Fim de Semana:** A solução definitiva para garantir a nossa quadra de vôlei todo sábado, sem estresse, sem esquecimento e sem a clássica pergunta *"alguém já reservou?"*.

🌐 **Acesse nosso Dashboard Oficial:** [reserva-volei-osvaldo.streamlit.app](https://reserva-volei-osvaldo.streamlit.app/)

---

## 📖 A História do Projeto

Nossa squad de vôlei tinha um problema crônico: **a reserva da quadra da Praça Osvaldo**. 
Sempre deixávamos para a última hora, esquecíamos de entrar no site da prefeitura ou rolava aquela confusão no grupo do WhatsApp para saber quem tinha conseguido pegar os horários.

Para resolver isso de uma vez por todas, este projeto nasceu. Ele é o nosso próprio "assistente virtual" e painel de controle, garantindo que sempre teremos quadra para jogar.

---

## 📊 Nosso Dashboard (Streamlit Cloud)

Para que todos da equipe saibam exatamente quando vamos jogar, o projeto conta com um portal online hospedado na nuvem pelo **Streamlit Cloud**.

* **Onde fica?** [Neste link aqui.](https://reserva-volei-osvaldo.streamlit.app/)
* **O que ele faz?** Ele lê automaticamente os dados atualizados pelo nosso robô e cria uma interface super moderna (com pegada esportiva/neon). Ele mostra quantas horas conseguimos, em quais dias e o intervalo exato de cada jogo (ex: *14h - 15h*). 
* É só salvar o link no celular e consultar quando quiser!

---

## ⚙️ Como a Mágica Funciona (Por Trás dos Panos)

O sistema opera 100% na nuvem, de forma invisível. Ninguém precisa acordar cedo ou deixar o computador ligado. Ele é dividido em três passos:

### 🤖 1. O Bot "Caçador de Horários" (GitHub Actions)
A cada intervalo de tempo, o **GitHub Actions** acorda nosso robô (feito em Python). Usando a biblioteca **Playwright**, o robô navega de forma invisível pelo portal de esportes da prefeitura e vasculha os próximos 4 sábados.

### 🧠 2. A Inteligência de Escolha
O bot não sai pegando qualquer horário. Ele tem uma **lista de prioridades** que nós definimos. 
Ele sempre tenta primeiro as nossas janelas favoritas de 3 horas (geralmente mais pro final da tarde). 
* *E se alguém já pegou a quadra?* Sem problema! O robô é inteligente e aciona o "Plano B", procurando horários mais cedo ou reduzindo o tempo de jogo para blocos menores (mínimo de 2 horas), garantindo que a gente não fique sem jogar.

### 💾 3. Salvando as Reservas
Quando o bot consegue reservar, ele usa inteligentemente as contas cadastradas da nossa equipe (uma conta por hora). Terminando o processo, ele anota tudo em um arquivo chamado `state.json` e salva automaticamente aqui no GitHub. 
O Dashboard no Streamlit percebe que esse arquivo mudou e atualiza a tela na mesma hora para todos nós!

---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.11
* **Frontend / Dashboard:** Streamlit & Custom CSS (Hospedado no Streamlit Cloud)
* **Web Automação:** Playwright (Chromium *headless*)
* **Infraestrutura do Bot:** GitHub Actions (CRON Jobs)
* **Banco de Dados:** Arquivo `.json` sincronizado via Git.

---
*Feito com ❤️, código e muito suor na quadra.*