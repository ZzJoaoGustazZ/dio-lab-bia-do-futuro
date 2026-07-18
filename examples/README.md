# Exemplos de Uso

Trechos de conversas reais com o Vero durante os testes, usando os dados fictícios de `data/` (cliente João Silva). Servem como referência do comportamento esperado do agente — os exemplos completos com raciocínio estão em [`docs/03-prompts.md`](../docs/03-prompts.md).

## Exemplo rápido

**Cliente:** Quanto eu gastei com alimentação esse mês?

**Vero:** Somando as transações de outubro na categoria alimentação (Supermercado + Restaurante), você gastou R$ 570,00. Isso representa cerca de 11% da sua renda mensal de R$ 5.000. Quer que eu compare com as outras categorias de gasto?

---

**Cliente:** Onde eu devo investir meu dinheiro?

**Vero:** Para te indicar algo com responsabilidade, preciso entender melhor a situação: esse valor é para uma meta específica ou é dinheiro livre? E qual o prazo que você imagina deixar aplicado?

---

Veja o código completo da aplicação em [`src/`](../src/).
