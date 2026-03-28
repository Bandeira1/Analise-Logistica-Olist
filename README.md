# Análise Estratégica de Logística e Retenção — Olist

Projeto de Parceria Semantix | Curso de Data Analytics

---

## Sumário

1. [Sobre o Projeto](#1-sobre-o-projeto)
2. [Fontes de Dados](#2-fontes-de-dados)
3. [Coleta de Dados](#3-coleta-de-dados)
4. [Modelagem e Análise Exploratória](#4-modelagem-e-análise-exploratória)
5. [Principais Insights](#5-principais-insights)
6. [Visualizações](#6-visualizações)
7. [Conclusões e Recomendações](#7-conclusões-e-recomendações)
8. [Como Executar](#8-como-executar)

---

## 1. Sobre o Projeto

### O problema

O crescimento do e-commerce brasileiro na última década trouxe junto um desafio que ainda não foi bem resolvido: a logística de entrega. Atrasos são frequentes, afetam milhões de consumidores e raramente são tratados com a profundidade que merecem. Boa parte das empresas do setor sabe que o problema existe, mas não tem clareza sobre onde ele está concentrado, qual é o custo real e quem está sendo mais prejudicado.

Este projeto nasceu dessa inquietação. Usando os dados reais da Olist — plataforma que conecta pequenos lojistas a grandes marketplaces no Brasil —, o objetivo foi ir além do diagnóstico superficial e entender os padrões por trás dos atrasos: quando eles acontecem, onde se concentram geograficamente, quanto custam para o negócio e o que significam para a fidelização de clientes.

### Por que isso importa

A experiência de entrega é um dos momentos mais críticos da jornada de compra online. Quando ela falha, o impacto não se limita à reclamação imediata. Clientes que sofreram atraso na primeira compra têm probabilidade significativamente menor de voltar — e isso representa uma perda de valor que não aparece diretamente no relatório financeiro do mês, mas corrói a base de clientes ao longo do tempo.

Além disso, o problema tem uma dimensão geográfica clara: estados do Norte e Nordeste do Brasil são desproporcionalmente afetados, o que levanta questões sobre equidade no acesso ao comércio digital e sobre a qualidade dos parceiros logísticos nessas regiões.

### Como a análise de dados contribui

Transformar um problema como esse em algo acionável exige dados. Com eles, é possível sair de afirmações genéricas — "as entregas estão atrasando muito" — para diagnósticos precisos: em qual mês a taxa de atraso dobrou, quais estados precisam de atenção imediata, quanto da receita está em risco e qual perfil de pedido tem maior probabilidade de chegar fora do prazo. Esse nível de detalhe é o que permite tomar decisões melhores — seja renegociando contratos com transportadoras, ajustando prazos estimados ou priorizando investimentos operacionais.

---

## 2. Fontes de Dados

O projeto utiliza exclusivamente dados públicos disponibilizados pela Olist no Kaggle.

| Atributo | Detalhe |
|---|---|
| Nome | Brazilian E-Commerce Public Dataset by Olist |
| Fonte | [Kaggle — olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) |
| Tipo de dado | Estruturado (CSV) |
| Licença | CC BY-NC-SA 4.0 |
| Período coberto | 2016 a 2018 |
| Volume | Aproximadamente 100.000 pedidos reais anonimizados |

### Arquivos utilizados

| Arquivo | Conteúdo | Campos principais |
|---|---|---|
| `olist_orders_dataset.csv` | Pedidos com todos os timestamps do ciclo de vida | `order_id`, `customer_id`, datas de compra, aprovação, despacho e entrega, status |
| `olist_customers_dataset.csv` | Localização dos clientes | `customer_id`, `customer_state`, `customer_city` |
| `olist_order_items_dataset.csv` | Itens por pedido com valores | `order_id`, `price`, `freight_value` |

---

## 3. Coleta de Dados

Os dados podem ser obtidos de duas formas:

**Via Kaggle API:**

```bash
pip install kaggle
kaggle datasets download -d olistbr/brazilian-ecommerce
unzip brazilian-ecommerce.zip -d bancos/
```

**Via download direto:**

Acesse a [página do dataset no Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), faça o download dos arquivos e salve-os na pasta `bancos/` na raiz do projeto.

Nenhum dado sensível ou privado foi utilizado. Todos os registros são anonimizados e de uso livre para fins educacionais, respeitando os termos da licença CC BY-NC-SA 4.0.

---

## 4. Modelagem e Análise Exploratória

### Pipeline geral

O processamento foi inteiramente implementado em Python, seguindo um pipeline linear e reproduzível:

```
Carga dos CSVs
    → Renomeação e padronização das colunas
    → Conversão de tipos (datas, numéricos)
    → Merge das três tabelas por chave relacional
    → Engenharia de features (tempo de entrega, flag de atraso, receita por pedido)
    → Cálculo de KPIs e análises segmentadas
    → Exportação dos gráficos
```

### Limpeza e pré-processamento

As colunas foram renomeadas para português para tornar o código mais legível. As colunas de data foram convertidas com `pd.to_datetime()`, permitindo calcular intervalos e SLAs. Pedidos com status cancelado ou sem data de entrega registrada foram excluídos das análises de atraso para evitar distorções.

### Engenharia de features

A lógica central do projeto depende de algumas variáveis calculadas a partir das datas brutas:

| Feature | Descrição | Como foi calculada |
|---|---|---|
| `tempo_entrega_dias` | Dias entre a compra e a entrega real | `data_entregue_cliente - data_compra` |
| `tempo_estimado_dias` | Dias entre a compra e o prazo prometido | `data_estimada_entrega - data_compra` |
| `atrasado` | Indica se o pedido chegou após o prazo | `data_entregue_cliente > data_estimada_entrega` |
| `diferenca_prazo` | Quantos dias o pedido ultrapassou o prazo | `tempo_entrega_dias - tempo_estimado_dias` |
| `receita_total` | Receita por pedido somando produto e frete | `SUM(preco + freight_value)` agrupado por `order_id` |

### Detecção de outliers

Para identificar pedidos com preços atipicamente altos, foi aplicado o método IQR (Interquartile Range):

```python
Q1 = itens['preco'].quantile(0.25)
Q3 = itens['preco'].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR
outliers = itens[itens['preco'] > limite_superior]
```

Esses pedidos foram analisados separadamente para verificar se o valor do produto influencia a probabilidade de atraso — e os resultados confirmaram que sim.

### Tecnologias utilizadas

| Ferramenta | Finalidade |
|---|---|
| Python 3.x | Linguagem principal |
| Pandas | Manipulação e transformação dos dados |
| Matplotlib | Geração de gráficos |
| Seaborn | Visualizações estatísticas |
| Datetime | Cálculos de SLA e análise temporal |
| Logging | Rastreabilidade de cada etapa do pipeline |

---

## 5. Principais Insights

**8,53% da receita total está vinculada a pedidos com atraso**

Em valores absolutos, isso representa aproximadamente R$ 1,35 milhão. Não é um problema marginal — mais de 1 em cada 10 reais movimentados na plataforma está associado a uma experiência de entrega negativa, o que por si só já justifica atenção operacional e investimento em melhorias.

**Pedidos de alto valor têm maior taxa de atraso**

Usando o método IQR para separar pedidos com preços fora do padrão, identificamos que esses pedidos têm taxa de atraso de 9,71% contra 7,71% nos demais. É um padrão contraintuitivo: os clientes que mais gastam são os que mais sofrem com atrasos — e provavelmente os que têm maior expectativa em relação ao serviço.

**O pico de atrasos não aconteceu na Black Friday**

Março de 2018 registrou taxa de atraso de 20,7%, superando novembro de 2017 (13,8%), o mês da Black Friday. Isso indica que o colapso logístico não seguiu o calendário comercial esperado — possivelmente refletindo um aumento de volume que excedeu a capacidade das transportadoras naquele período específico. O dado reforça que o monitoramento precisa ser contínuo, não concentrado apenas em datas de pico previstas.

**Alagoas lidera o ranking de atrasos com 23%**

Os estados do Nordeste e Norte concentram as maiores taxas de atraso percentual. Alagoas (23%), seguida de outros estados da região, deixa claro que o problema tem raízes geográficas e estruturais — e que uma solução nacional uniforme não é suficiente.

**Pedidos atrasados têm ticket médio R$ 13,16 superior**

Além de mais frequentes em pedidos de alto valor, os atrasos acontecem em transações com ticket médio mais alto. Isso amplifica o impacto financeiro e o risco de perda de clientes justamente no segmento mais lucrativo.

**Um atraso na primeira compra reduz em 20% a taxa de retorno do cliente**

Este foi o achado de maior peso estratégico da análise. A primeira experiência de entrega é determinante para a decisão de recompra. Clientes que sofreram atraso logo na estreia têm probabilidade 20 pontos percentuais menor de voltar — uma perda de LTV que não aparece em nenhum relatório imediato, mas tem efeito composto significativo sobre a base ao longo do tempo.

**2,3 dias de gap entre aprovação do pagamento e despacho**

Antes mesmo de entrar na transportadora, o pedido espera 2,3 dias em média para ser despachado após a aprovação do pagamento. Esse é um gargalo interno — controlável pela operação da plataforma — que contribui para o atraso final sem depender de terceiros.

---

## 6. Visualizações

Os gráficos gerados pelo script estão disponíveis na pasta [`/Graficos`](./Graficos/) do repositório.

| Arquivo | O que mostra |
|---|---|
| `taxa_atraso_estado.png` | Top 10 estados por taxa percentual de atraso |
| `receita_impactada.png` | Receita total versus receita vinculada a pedidos com atraso |
| `outlier_vs_normal.png` | Comparação da taxa de atraso entre pedidos de alto valor e demais |
| `distribuicao_preco.png` | Distribuição de preços com marcação do limiar de outlier |
| `receita_total_vs_atraso.png` | Evolução temporal da receita impactada |
| `ticket_medio.png` | Ticket médio comparativo entre pedidos no prazo e atrasados |
| `sazonalidade.png` | Taxa mensal de atraso ao longo de todo o período analisado |
| `gargalos.png` | Tempos médios de aprovação e despacho |

Dashboard interativo: [Acesse o Looker Studio](https://lookerstudio.google.com/reporting/465991c2-4e21-4e44-8067-efa2f1b99d33)

---

## 7. Conclusões e Recomendações

A análise confirmou que os atrasos na Olist não são um problema aleatório ou uniforme. Eles têm padrão geográfico, sazonalidade irregular, impacto financeiro mensurável e consequência direta na retenção de clientes.

O impacto financeiro é real e concentrado. Mais de 8,5% da receita está associada a pedidos com atraso, e esse percentual é maior entre os pedidos de maior valor — o que significa que o problema está corroendo justamente o segmento mais lucrativo da base.

A retenção de clientes é o risco mais silencioso. A queda de 20% na taxa de retorno após um atraso na primeira compra não aparece em nenhum relatório imediato, mas tem efeito composto sobre o LTV da base ao longo do tempo.

A concentração geográfica indica problemas estruturais. Estados como AL, MA e RO apresentam taxas de atraso sistematicamente superiores à média, o que aponta para fragilidades nos parceiros logísticos dessas regiões — e não apenas para variações pontuais de demanda.

Existe um gargalo interno que pode ser resolvido sem depender de terceiros. Os 2,3 dias de espera entre aprovação e despacho são responsabilidade operacional da plataforma e representam uma oportunidade de melhoria imediata.

Com base nesses achados, as ações mais relevantes seriam revisar contratos e SLAs com transportadoras nos estados com maior taxa de atraso (AL, MA, RO, PA), implementar alertas automáticos de monitoramento quando a taxa de atraso ultrapassar um limiar definido por estado ou período, criar um tratamento diferenciado para a primeira entrega de novos clientes dado o impacto comprovado na retenção, automatizar o processo interno de despacho para eliminar o gap de 2,3 dias pós-aprovação, e desenvolver um modelo preditivo de risco de atraso por pedido — permitindo ação preventiva antes que o problema ocorra.

---

## 8. Como Executar

```bash
# Clone o repositório
git clone https://github.com/Bandeira1/Analise-Logistica-Olist.git
cd Analise-Logistica-Olist

# Instale as dependências
pip install pandas matplotlib seaborn

# Adicione os dados da Olist na pasta /bancos
# Download disponível em: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

# Execute o pipeline
python analise_logistica_usuario.py
```

Os gráficos serão gerados automaticamente na pasta `graficos/` ao final da execução.

---

Projeto desenvolvido como entrega do Projeto de Parceria Semantix — Curso de Data Analytics.  
Dados: Brazilian E-Commerce Public Dataset by Olist (Kaggle, CC BY-NC-SA 4.0).
