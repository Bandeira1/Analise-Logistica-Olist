# Análise Estratégica de Logística e Retenção - Olist 🚚📊

Este projeto apresenta uma análise profunda dos dados de e-commerce da Olist, focando em identificar gargalos logísticos, o impacto financeiro dos atrasos e como a experiência de entrega afeta a retenção de clientes.

## 🚀 Destaques do Projeto
- **Impacto no LTV:** Provamos que um atraso na primeira entrega reduz a taxa de retorno do cliente em **20%**.
- **Análise Financeira:** Identificamos que **8.53% da receita total** (R$ 1.35M) está vinculada a pedidos com atraso.
- **Detecção de Outliers:** Uso de estatística (IQR) para provar que pedidos de alto valor têm **9.71% de taxa de atraso** vs 7.71% em pedidos normais.
- **Gargalos Operacionais:** Identificação de um tempo médio de **2.3 dias** apenas para o despacho após a aprovação.

## 🛠️ Stack Tecnológica
- **Linguagem:** Python 3.x
- **Bibliotecas:** 
  - `Pandas`: Manipulação e tratamento de dados.
  - `Matplotlib` & `Seaborn`: Visualização de dados e criação de gráficos.
  - `Datetime`: Cálculos de SLAs e sazonalidade.

## 📂 Estrutura do Código
- `analise_logistica_usuario.py`: Pipeline principal (Carga -> Tratamento -> Features -> KPIs -> Análises).
- `visualizacao.py`: Script modular contendo todas as funções de geração de gráficos.
- `graficos/`: Pasta contendo as visualizações exportadas em PNG.

## 📈 Principais Insights Extraídos
1. **Sazonalidade Crítica:** Março de 2018 apresentou o maior pico de atrasos (**20.7%**), superando até o mês da Black Friday (**13.8%**).
2. **Geografia do Atraso:** Alagoas (AL) lidera o ranking de atrasos percentuais com **23%**, exigindo revisão imediata de parceiros logísticos na região.
3. **Ticket Médio:** Pedidos atrasados possuem um ticket médio **R$ 13,16 superior** aos pedidos no prazo, indicando que os clientes mais valiosos estão sendo os mais prejudicados.

## ⚙️ Como Executar
1. Certifique-se de ter os datasets da Olist na pasta `bancos/`.
2. Instale as dependências: `pip install pandas matplotlib seaborn`.
3. Execute o script principal: `python analise_logistica_usuario.py`.

---
*Projeto desenvolvido como parte de um estudo aprofundado em Data Analytics e Business Intelligence.*
