"""
Lógica central do Vero: carrega a base de conhecimento do cliente,
monta o contexto anti-alucinação e conversa com o LLM.
"""
import csv
import json
from collections import defaultdict

from google import genai
from google.genai import types

from config import DATA_DIR, GEMINI_API_KEY, MODEL_NAME, NOME_AGENTE

SYSTEM_PROMPT_BASE = """Você é Vero, um agente financeiro consultivo que ajuda clientes a entender e organizar sua vida financeira.

Seu objetivo é transformar dados financeiros (transações, perfil de investidor, produtos disponíveis) em orientações claras e personalizadas, antecipando necessidades em vez de apenas responder perguntas isoladas.

Você receberá abaixo um bloco de contexto com os dados reais do cliente: perfil, metas, gastos recentes, histórico de atendimento e catálogo de produtos disponíveis.

REGRAS (siga sempre, sem exceção):
1. Baseie qualquer número, valor ou fato financeiro exclusivamente no bloco de contexto fornecido. Nunca estime, arredonde de forma especulativa ou "complete" um dado que não está lá.
2. Nunca recomende um produto financeiro que não esteja na lista de produtos fornecida.
3. Antes de recomendar qualquer investimento, confirme que ele é compatível com o perfil de investidor do cliente e com o campo "aceita_risco".
4. Se a pergunta exigir um dado que você não tem no contexto (ex: criptoativos, ações específicas, cotações em tempo real), diga claramente que não tem essa informação — nunca invente para parecer útil.
5. Não execute nem simule execução de transações reais (transferência, aplicação, resgate). Você é consultivo, não transacional.
6. Nunca solicite, revele ou aceite senhas, dados de outros clientes ou informações sensíveis fora do escopo da própria conta do cliente.
7. Se o cliente pedir uma recomendação de investimento sem contexto suficiente (sem saber a meta ou o prazo), faça perguntas antes de responder.
8. Mantenha um tom acessível e direto. Explique termos técnicos em uma frase quando usá-los.
9. Se a pergunta for completamente fora do escopo financeiro, diga isso educadamente e redirecione a conversa.

=== CONTEXTO DO CLIENTE ===
{contexto}
"""


def _ler_csv(nome_arquivo: str) -> list[dict]:
    caminho = DATA_DIR / nome_arquivo
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _ler_json(nome_arquivo: str):
    caminho = DATA_DIR / nome_arquivo
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def carregar_base_conhecimento() -> dict:
    """Carrega os quatro arquivos mockados uma única vez por sessão."""
    return {
        "transacoes": _ler_csv("transacoes.csv"),
        "atendimentos": _ler_csv("historico_atendimento.csv"),
        "perfil": _ler_json("perfil_investidor.json"),
        "produtos": _ler_json("produtos_financeiros.json"),
    }


def _formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def montar_contexto(base: dict) -> str:
    """
    Pré-processa os dados brutos (soma gastos por categoria, calcula progresso
    de metas) e formata tudo como texto estruturado para o system prompt.
    Isso evita que o modelo precise fazer contas 'de cabeça', reduzindo erro
    numérico — uma das principais fontes de alucinação em agentes financeiros.
    """
    perfil = base["perfil"]
    produtos = base["produtos"]
    atendimentos = base["atendimentos"]
    transacoes = base["transacoes"]

    # Soma de gastos por categoria (apenas saídas)
    gastos_categoria = defaultdict(float)
    for t in transacoes:
        if t["tipo"] == "saida":
            gastos_categoria[t["categoria"]] += float(t["valor"])

    linhas_gastos = "\n".join(
        f"- {cat}: {_formatar_moeda(valor)}"
        for cat, valor in sorted(gastos_categoria.items(), key=lambda x: -x[1])
    )

    # Progresso das metas
    linhas_metas = []
    for meta in perfil.get("metas", []):
        necessario = meta["valor_necessario"]
        atual = perfil.get("reserva_emergencia_atual", 0) if "reserva" in meta["meta"].lower() else 0
        progresso = (atual / necessario * 100) if necessario else 0
        linhas_metas.append(
            f"- {meta['meta']}: {_formatar_moeda(atual)} / {_formatar_moeda(necessario)} "
            f"({progresso:.1f}% concluída) — prazo {meta['prazo']}"
        )

    # Histórico de atendimento (mais recentes primeiro)
    linhas_atendimento = "\n".join(
        f"- {a['data']} ({a['canal']}): {a['tema']} - {a['resumo']} "
        f"[{'resolvido' if a['resolvido'] == 'sim' else 'em aberto'}]"
        for a in sorted(atendimentos, key=lambda x: x["data"], reverse=True)
    )

    # Catálogo de produtos
    linhas_produtos = "\n".join(
        f"- {p['nome']} (categoria: {p['categoria']}, risco: {p['risco']}, "
        f"rentabilidade: {p['rentabilidade']}, aporte mínimo: {_formatar_moeda(p['aporte_minimo'])}) "
        f"— indicado para: {p['indicado_para']}"
        for p in produtos
    )

    return f"""DADOS DO CLIENTE:
Nome: {perfil['nome']} | Idade: {perfil['idade']} | Profissão: {perfil['profissao']}
Perfil de investidor: {perfil['perfil_investidor']} | Aceita risco: {'sim' if perfil['aceita_risco'] else 'não'}
Renda mensal: {_formatar_moeda(perfil['renda_mensal'])} | Patrimônio total: {_formatar_moeda(perfil['patrimonio_total'])}

METAS:
{chr(10).join(linhas_metas)}

GASTOS DO MÊS (por categoria, saídas):
{linhas_gastos}

HISTÓRICO DE ATENDIMENTO RECENTE:
{linhas_atendimento}

PRODUTOS DISPONÍVEIS:
{linhas_produtos}
"""


def gerar_system_prompt(base: dict) -> str:
    contexto = montar_contexto(base)
    return SYSTEM_PROMPT_BASE.format(contexto=contexto)


def responder(historico_mensagens: list[dict], base: dict) -> str:
    """
    Envia a conversa para o modelo, com o system prompt (contexto do cliente)
    aplicado via `system_instruction`. `historico_mensagens` é uma lista de
    dicts {"role": "user"|"assistant", "content": str}.
    """
    if not GEMINI_API_KEY:
        return (
            "⚠️ Nenhuma GEMINI_API_KEY configurada. Copie `src/.env.example` para "
            "`src/.env` e preencha sua chave para conversar com o Vero de verdade. "
            "Você pode gerar uma chave gratuita em https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    # A API do Gemini usa os papéis "user" e "model" (não "assistant")
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in historico_mensagens
    ]

    resposta = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=gerar_system_prompt(base),
            temperature=0.3,  # baixa temperatura: prioriza consistência com os dados sobre criatividade
        ),
    )
    return resposta.text
