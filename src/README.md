# src — Aplicação do Vero

Código do agente financeiro Vero.

```
src/
├── app.py              # Interface de chat (Streamlit)
├── agente.py           # Carregamento de dados, montagem de contexto e chamada ao LLM
├── config.py            # Configuração e variáveis de ambiente
├── requirements.txt
└── .env.example
```

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # preencha GEMINI_API_KEY (gere em aistudio.google.com/apikey)
streamlit run app.py
```

O agente carrega automaticamente os dados fictícios de `../data/` (cliente João Silva) e responde apenas com base neles — veja as regras completas em `../docs/03-prompts.md`.
