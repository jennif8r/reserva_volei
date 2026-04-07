<div align="center">
<br/><br/>

<!-- BANNER ANIMADO COM GRADIENTE -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=blur&height=300&color=gradient&text=V%C3%B4lei%20Pra%C3%A7a%20Osvaldo&section=header&reversal=true&fontColor=B44A4&textBg=false&animation=fadeIn&stroke=4F4BD2&desc=Bot%20Aut%C3%B4nomo%20e%20Hub%20da%20Equipe&descAlign=50&descAlignY=64&descSize=17.9" alt="header"/>

<!-- TYPING SVG ELEGANTE -->
<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Chakra+Petch&weight=600&size=20&duration=3000&pause=1000&color=FF0055&center=true&vCenter=true&multiline=false&width=700&lines=Fim+da+confus%C3%A3o+para+garantir+a+quadra.;Automa%C3%A7%C3%A3o+inteligente+e+silenciosa+na+nuvem.;Bot+Ca%C3%A7ador+de+Hor%C3%A1rios+%E2%80%A2+Playwright.;Analytics+e+Dashboard+com+Streamlit." alt="Typing SVG" />
</a>

<br/><br/>

<!-- METADADOS STATUS / FOCO -->
<p align="center">
  <a href="https://reserva-volei-osvaldo.streamlit.app/"><img src="https://img.shields.io/badge/Acessar-Dashboard_Oficial-FF0055?style=for-the-badge&logo=streamlit&logoColor=white" alt="Dashboard Oficial"/></a>
  <img src="https://img.shields.io/badge/Status-Ativo_e_Operacional-22C55E?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Status"/>
  <img src="https://img.shields.io/badge/Tech_Foco-Automação%20%26%20Cloud-A855F7?style=for-the-badge&logo=python&logoColor=white" alt="Foco"/>
</p>

<br/>

<!-- START: INOVATIVE DASHBOARD BUTTON -->
<a href="https://reserva-volei-osvaldo.streamlit.app/">
  <table align="center" style="border-collapse: collapse; border: 2px solid #FF0055; background-color: #0d1117; border-radius: 10px;">
    <tr>
      <td align="center" style="padding: 15px 40px;">
        <img src="https://readme-typing-svg.demolab.com?font=Chakra+Petch&weight=800&size=28&pause=1000&color=FF0055&center=true&vCenter=true&width=350&height=40&lines=❖+ACESSAR+DASHBOARD;❖+ENTRAR+NO+HUB;❖+CONSULTAR+RESERVAS" alt="CTA" />
        <br/>
        <img src="https://img.shields.io/badge/Status-ONLINE-22C55E?style=for-the-badge&logo=stream" alt="Online" style="margin-bottom: 5px;"/>
        <br/>
        <samp style="color: #C9D1D9; font-size: 13px;">🔗 reserva-volei-osvaldo.streamlit.app</samp>
      </td>
    </tr>
  </table>
</a>
<!-- END: INOVATIVE DASHBOARD BUTTON -->

</div>

<br/><br/>

---

## 🏐 O Valor do Produto

Nossa *squad* de vôlei enfrentava um problema crônico de gestão esportiva: **a escalação e reserva de quadras aos sábados**. A dependência de ações manuais resultava em esquecimentos, janelas de horário perdidas e ruído na comunicação.

O **Bot e Hub da Praça Osvaldo** foi desenvolvido para mudar esse cenário, proporcionando:
- **Zero Atrito:** Garantia de disponibilidade da quadra sem acordar cedo ou depender da memória humana.
- **Transparência Compartilhada:** Todos da equipe têm acesso a um *dashboard* com as horas garantidas, o saldo de vitórias semanais do bot e os dias programados.
- **Inteligência Descentralizada:** Um "Plano B" autônomo. Se a quadra ideal já estiver ocupada, o bot executa matrizes de decisão para salvar blocos esportivos menores ou adaptar o cronograma.

---

<div align="center">
<br/>

<p align="center"><strong><samp> Engenharia de Automação & Robô Autônomo </samp></strong></p>

<img height="34" src="https://img.shields.io/badge/Python-0D1117?style=flat-square&logo=python&logoColor=3776AB"/>
<img height="34" src="https://img.shields.io/badge/Playwright_(Headless)-0D1117?style=flat-square&logo=playwright&logoColor=2EAD33"/>
<img height="34" src="https://img.shields.io/badge/GitHub_Actions_(CRON)-0D1117?style=flat-square&logo=githubactions&logoColor=2088FF"/>
<img height="34" src="https://img.shields.io/badge/State_Management-JSON-0D1117?style=flat-square&logo=json&logoColor=white"/>

<br/><br/>

<p align="center"><strong><samp> Analytics, UX & Hospedagem </samp></strong></p>

<img height="34" src="https://img.shields.io/badge/Streamlit-0D1117?style=flat-square&logo=streamlit&logoColor=FF4B4B"/>
<img height="34" src="https://img.shields.io/badge/Streamlit_Cloud-0D1117?style=flat-square&logo=icloud&logoColor=White"/>
<img height="34" src="https://img.shields.io/badge/Pandas-0D1117?style=flat-square&logo=pandas&logoColor=150458"/>

</div>

<br/>

---

## ⚙️ Arquitetura e Nível de Automação

O sistema foi arquitetado para ser uma solução "hands-off" (zero intervenção manual), operando de maneira "invisível" com orquestração completa em nuvem.

### O Fluxo de Execução Silenciosa:

1. **Trigger Baseado em Tempo:** O **GitHub Actions** dispara *jobs* periódicos via sistema de *cron*. 
2. **Scraping e Caça de Horários:** O robô Python usa o **Playwright** em modo *headless* para navegar ao portal de reservas e analisar os próximos 4 sábados disponíveis.
3. **Motor de Decisão (Fallback System):** O bot detém a capacidade de avaliar o terreno. Ele tenta fechar a janela máxima otimizada, porém se o sistema detectar disponibilidade parcial, ele complementa um turno já aberto por outra conta.
4. **Multiplexação de Contas:** Empregando um *pool* dinâmico de contas da equipe (1 hora por conta), ele burla de forma inteligente as restrições logísticas do site.
5. **State GitOps:** Atualiza um repositório central (`state.json`) efetuando *commit* dos resultados adquiridos.
6. **Frontend Reativo:** O webhook do repositório notifica o **Streamlit Cloud**, reiniciando e propagando as vitórias para as interfaces *mobile* da galera em tempo real!

```mermaid
graph TD
    A([🕒 CRON GitHub Actions]) -->|Acorda o Bot| B(Robô Python)
    B -->|Busca Headless| C[Portal da Prefeitura]
    C -->|Rastreia Disponibilidade| D{Existem horas vazias?}
    D -- Sim --> E[Algoritmo de Prioridade/Janelas]
    D -- Não --> Z[Dorme e Tenta Mais Tarde]
    E -->|Usa Pool de Contas| F[Efetua as Reservas]
    F -->|Salva| G[(state.json no GitHub)]
    G -->|Webhook Trigger| H[Streamlit UI Updates]
    H -->|Exibe na Tela| I((Dashboard da Equipe))
```

---

<div align="center">

<br/>

<!-- FOOTER WAVE MÍSTICO -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:3b52b5,50:bb0055,100:0b1117&height=120&section=footer" alt="footer"/>

</div>