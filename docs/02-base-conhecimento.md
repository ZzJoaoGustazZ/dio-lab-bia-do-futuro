# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Dá contexto sobre dúvidas e temas que o cliente já trouxe antes, evitando repetir explicações já dadas |
| `perfil_investidor.json` | JSON | Base para personalizar qualquer recomendação — perfil de risco, renda, metas e prazos |
| `produtos_financeiros.json` | JSON | Único catálogo de produtos que o agente pode citar; nada fora dele é mencionado |
| `transacoes.csv` | CSV | Usado para responder perguntas sobre gastos, categorias e fluxo de caixa do mês |

Todos os quatro arquivos mockados originais foram mantidos como estão, representando um único cliente fictício (João Silva) usado como caso de demonstração ao longo de toda a documentação.

---

## Adaptações nos Dados

Os dados foram mantidos no formato original. A adaptação ficou concentrada na camada de **integração**: em vez de simplesmente injetar os arquivos brutos no prompt, `agente.py` faz um pré-processamento:

- Nas transações, calcula automaticamente o total de saídas por categoria (ex: total gasto em alimentação no mês), para que o modelo não precise somar valores "de cabeça" — isso reduz erro de aritmética, uma fonte comum de alucinação numérica em LLMs.
- No perfil do investidor, calcula o percentual de progresso de cada meta (`reserva_emergencia_atual` vs `valor_necessario`) antes de mandar para o prompt.

## Estratégia de Integração

### Como os dados são carregados?
Os quatro arquivos são carregados uma única vez no início da sessão do Streamlit (função `carregar_base_conhecimento()` em `agente.py`) e mantidos em `st.session_state`, evitando releitura do disco a cada mensagem.

### Como os dados são usados no prompt?
Os dados entram no **system prompt**, como um bloco de contexto estruturado, e não são reenviados como mensagens separadas. Isso mantém o modelo sempre "com a base na mão" sem que o cliente precise repetir informações. Como a base é pequena (um único cliente mockado), ela cabe inteira no contexto — em um cenário de produção com múltiplos clientes, o correto seria buscar (via RAG ou consulta a banco de dados) apenas os dados do cliente autenticado na sessão.

---

## Exemplo de Contexto Montado

```
=== DADOS DO CLIENTE ===
Nome: João Silva | Idade: 32 | Profissão: Analista de Sistemas
Perfil de investidor: moderado | Aceita risco: não
Renda mensal: R$ 5.000,00 | Patrimônio total: R$ 15.000,00

=== METAS ===
- Completar reserva de emergência: R$ 10.000,00 / R$ 15.000,00 (66,7% concluída) — prazo 2026-06
- Entrada do apartamento: R$ 0,00 / R$ 50.000,00 (0% concluída) — prazo 2027-12

=== GASTOS DO MÊS (por categoria) ===
- moradia: R$ 1.380,00
- alimentacao: R$ 570,00
- transporte: R$ 295,00
- saude: R$ 188,00
- lazer: R$ 55,90

=== HISTÓRICO DE ATENDIMENTO RECENTE ===
- 2025-10-25 (email): Atualização cadastral - resolvido
- 2025-10-12 (chat): Metas financeiras - acompanhamento da reserva de emergência
- 2025-10-01 (chat): Dúvida sobre Tesouro Selic - resolvido

=== PRODUTOS DISPONÍVEIS ===
- Tesouro Selic (risco baixo, 100% da Selic, aporte mín. R$ 30) — indicado para reserva de emergência
- CDB Liquidez Diária (risco baixo, 102% do CDI, aporte mín. R$ 100)
- LCI/LCA (risco baixo, 95% do CDI, isento de IR, aporte mín. R$ 1.000)
- Fundo Multimercado (risco médio, CDI + 2%, aporte mín. R$ 500)
- Fundo de Ações (risco alto, rentabilidade variável, aporte mín. R$ 100)
```
