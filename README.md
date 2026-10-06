# 🌿 Vero — Agente Financeiro Inteligente

**Vero** é um agente de IA generativa voltado para consultoria financeira pessoal. Em vez de esperar o cliente perguntar, Vero analisa o histórico de transações, o perfil de investidor e as metas cadastradas para antecipar orientações relevantes, sempre ancorado nos dados reais do cliente — nunca em suposições.

O nome vem do latim *verus* ("verdadeiro"): o compromisso central do agente é nunca inventar números, produtos ou promessas de rentabilidade. Tudo que Vero diz é rastreável até uma fonte de dados concreta.

---

## Sumário

- [O problema que o Vero resolve](#o-problema-que-o-vero-resolve)
- [Documentação](#documentação)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como rodar](#como-rodar)
- [Stack utilizada](#stack-utilizada)

---

## O problema que o Vero resolve

A maioria dos apps de banco mostra dados — extrato, saldo, produtos — mas deixa a interpretação por conta do cliente. Quem não tem familiaridade com finanças fica sem saber: "isso é bom ou ruim pra mim?", "eu deveria estar investindo mais?", "esse produto faz sentido pro meu perfil?".

Vero funciona como uma camada consultiva sobre esses dados: conversa em linguagem natural, entende o contexto financeiro do cliente e devolve orientação personalizada — sempre citando de onde tirou a informação e admitindo abertamente quando não sabe algo.

---

## Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/01-documentacao-agente.md`](./docs/01-documentacao-agente.md) | Caso de uso, persona, arquitetura e estratégia anti-alucinação |
| [`docs/02-base-conhecimento.md`](./docs/02-base-conhecimento.md) | Como os dados do cliente viram contexto para o modelo |
| [`docs/03-prompts.md`](./docs/03-prompts.md) | System prompt completo, exemplos de interação e edge cases |
| [`docs/04-metricas.md`](./docs/04-metricas.md) | Como o agente foi avaliado e os resultados dos testes |
| [`docs/05-pitch.md`](./docs/05-pitch.md) | Roteiro de apresentação |

---

## Estrutura do repositório

```
📁 vero-agente-financeiro/
│
├── 📄 README.md
│
├── 📁 data/                          # Base de dados mockada do cliente
│   ├── historico_atendimento.csv
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   └── transacoes.csv
│
├── 📁 docs/                          # Documentação do agente
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
├── 📁 src/                           # Aplicação do agente (Streamlit)
│   ├── app.py                        # Interface do chat
│   ├── agente.py                     # Lógica do agente e montagem de contexto
│   ├── config.py                     # Configuração e variáveis de ambiente
│   ├── requirements.txt
│   └── .env.example
│
├── 📁 assets/                        # Diagramas e imagens
│
└── 📁 examples/                      # Exemplos de conversa com o Vero
```

---

## Como rodar

```bash
cd src
pip install -r requirements.txt
cp .env.example .env   # e preencha sua GEMINI_API_KEY
streamlit run app.py
```

---

## Stack utilizada

- **Interface:** Streamlit
- **LLM:** Gemini 3.5 Flash via API do Google (tem camada gratuita — [aistudio.google.com/apikey](https://aistudio.google.com/apikey)), facilmente trocável por outro provedor — ver `src/agente.py`
- **Base de conhecimento:** arquivos CSV/JSON locais, carregados e formatados como contexto a cada mensagem
- **Segurança:** system prompt restritivo + validação de que toda afirmação numérica tem origem nos dados carregados

---

## Licença e autoria

Projeto desenvolvido durante o Bootcamp Bradesco - GenAI, Dados & Cyber, utilizando uma implementação base fornecida pela DIO. O projeto foi posteriormente modificado e personalizado por mim, mantendo grande parte da estrutura original. Os dados em data/ são fictícios e utilizados para fins de demonstração.
