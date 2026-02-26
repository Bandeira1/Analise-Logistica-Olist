import pandas as pd
import logging
import os
from visualizacao import (
    grafico_taxa_atraso_estado,
    grafico_receita_impactada,
    grafico_outlier_vs_normal,
    grafico_distribuicao_preco,
    grafico_receita_total_vs_atraso,
    grafico_ticket_medio,
    grafico_sazonalidade,
    grafico_gargalos
)

# =====================================================
# CONFIGURAÇÃO DE LOGGING
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("execucao_analise.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIG PANDAS
# =====================================================
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# =====================================================
# LEITURA DOS DADOS
# =====================================================
def carregar_dados():
    try:
        logger.info("Iniciando carga dos arquivos CSV...")
        # Usando caminhos flexíveis para o ambiente
        path_base = 'bancos/' if os.path.exists('bancos/') else '/home/ubuntu/upload/'
        
        clientes = pd.read_csv(f'{path_base}olist_customers_dataset.csv')
        pedidos = pd.read_csv(f'{path_base}olist_orders_dataset.csv')
        itens = pd.read_csv(f'{path_base}olist_order_items_dataset.csv')
        
        logger.info("Carga de dados concluída com sucesso.")
        return clientes, pedidos, itens
    except Exception as e:
        logger.error(f"Falha crítica na carga de dados: {str(e)}")
        raise

# =====================================================
# TRATAMENTOS
# =====================================================
def tratar_clientes(clientes: pd.DataFrame) -> pd.DataFrame:
    logger.info("Tratando dados de clientes...")
    return clientes.rename(columns={
        'customer_id': 'id_cliente',
        'customer_unique_id': 'id_cliente_unico',
        'customer_zip_code_prefix': 'cep',
        'customer_city': 'cidade',
        'customer_state': 'estado'
    })

def tratar_pedidos(pedidos: pd.DataFrame) -> pd.DataFrame:
    logger.info("Tratando dados de pedidos...")
    pedidos = pedidos.rename(columns={
        'order_id': 'id_pedido',
        'customer_id': 'id_cliente',
        'order_status': 'status_pedido',
        'order_purchase_timestamp': 'data_compra',
        'order_delivered_customer_date': 'data_entregue_cliente',
        'order_estimated_delivery_date': 'data_estimada_entrega'
    })

    datas = ['data_compra', 'data_entregue_cliente', 'data_estimada_entrega']
    for data in datas:
        pedidos[data] = pd.to_datetime(pedidos[data])
    
    return pedidos

def tratar_itens(itens: pd.DataFrame) -> pd.DataFrame:
    logger.info("Tratando dados de itens...")
    itens = itens.rename(columns={
        'order_id': 'id_pedido',
        'order_item_id': 'id_item_pedido',
        'product_id': 'id_produto',
        'seller_id': 'id_vendedor',
        'shipping_limit_date': 'data_limite_envio',
        'price': 'preco',
        'freight_value': 'frete'
    })
    itens['data_limite_envio'] = pd.to_datetime(itens['data_limite_envio'])
    return itens

# =====================================================
# BASE ANALÍTICA E FEATURES
# =====================================================
def criar_base(clientes: pd.DataFrame, pedidos: pd.DataFrame) -> pd.DataFrame:
    logger.info("Realizando merge das bases de pedidos e clientes...")
    return pedidos.merge(clientes, on='id_cliente', how='left')

def criar_features(base: pd.DataFrame) -> pd.DataFrame:
    logger.info("Criando features temporais e flags de atraso...")
    base['tempo_entrega_dias'] = (base['data_entregue_cliente'] - base['data_compra']).dt.days
    base['tempo_estimado_dias'] = (base['data_estimada_entrega'] - base['data_compra']).dt.days
    base['atrasado'] = (base['data_entregue_cliente'] > base['data_estimada_entrega'])
    base['diferenca_prazo'] = (base['tempo_entrega_dias'] - base['tempo_estimado_dias'])
    return base

def adicionar_receita_pedido(base: pd.DataFrame, itens: pd.DataFrame) -> pd.DataFrame:
    logger.info("Adicionando informações de receita à base principal...")
    receita_por_pedido = (
        itens.groupby('id_pedido')[['preco', 'frete']]
        .sum()
        .assign(receita_total=lambda df: df['preco'] + df['frete'])
        .reset_index()
    )
    return base.merge(receita_por_pedido, on='id_pedido', how='left')

# =====================================================
# ANÁLISES TÉCNICAS
# =====================================================
def detectar_outliers(itens: pd.DataFrame) -> pd.DataFrame:
    logger.info("Executando detecção de outliers de preço (Método IQR)...")
    Q1 = itens['preco'].quantile(0.25)
    Q3 = itens['preco'].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + 1.5 * IQR
    return itens[itens['preco'] > limite_superior].sort_values('preco', ascending=False)

def analisar_outliers_logistica(base, outliers):
    ids_outliers = outliers['id_pedido'].unique()
    base_outliers = base[base['id_pedido'].isin(ids_outliers)]
    base_normal = base[~base['id_pedido'].isin(ids_outliers)]
    
    print("\n========= IMPACTO LOGÍSTICO DOS OUTLIERS =========")
    print(f"Taxa de atraso OUTLIERS: {base_outliers['atrasado'].mean() * 100:.2f}%")
    print(f"Taxa de atraso NORMAL: {base_normal['atrasado'].mean() * 100:.2f}%")

def impacto_financeiro_atrasos(base):
    receita_total = base['receita_total'].sum()
    receita_atrasada = base[base['atrasado'] == True]['receita_total'].sum()
    percentual_receita_afetada = (receita_atrasada / receita_total) * 100

    print("\n===== IMPACTO FINANCEIRO DOS ATRASOS =====")
    print(f"Receita total: R$ {receita_total:,.2f}")
    print(f"Receita com atraso: R$ {receita_atrasada:,.2f}")
    print(f"% da receita afetada: {percentual_receita_afetada:.2f}%")

def atraso_por_estado(base):
    resultado = base.groupby('estado')['atrasado'].mean().sort_values(ascending=False).head(10)
    print("\n===== TOP 10 ESTADOS COM MAIOR TAXA DE ATRASO =====")
    print((resultado * 100).round(2))

def impacto_financeiro_por_estado(base):
    impacto = base[base['atrasado'] == True].groupby('estado')['receita_total'].sum().sort_values(ascending=False).head(10)
    print("\n===== TOP 10 ESTADOS COM MAIOR RECEITA IMPACTADA =====")
    print(impacto)

def ticket_medio_por_status(base):
    resumo = base.groupby('atrasado')['receita_total'].mean()
    print("\n===== TICKET MÉDIO POR STATUS =====")
    print(f"No Prazo: R$ {resumo[False]:,.2f}")
    print(f"Atrasado: R$ {resumo[True]:,.2f}")
    print(f"Diferença média: R$ {resumo[True] - resumo[False]:,.2f}")

def analisar_sazonalidade(base):
    logger.info("Analisando tendências mensais (Sazonalidade)...")
    base['mes_ano'] = base['data_compra'].dt.to_period('M')
    tendencia = base.groupby('mes_ano')['atrasado'].mean() * 100
    print("\n===== ANÁLISE DE SAZONALIDADE (MENSAL) =====")
    print(tendencia.tail(12))
    return tendencia

def analisar_gargalos(pedidos: pd.DataFrame):
    logger.info("Analisando gargalos operacionais de aprovação e despacho...")
    # Garantindo conversão robusta para as colunas de data
    pedidos['order_approved_at'] = pd.to_datetime(pedidos['order_approved_at'], errors='coerce')
    pedidos['order_delivered_carrier_date'] = pd.to_datetime(pedidos['order_delivered_carrier_date'], errors='coerce')
    pedidos['order_purchase_timestamp'] = pd.to_datetime(pedidos['order_purchase_timestamp'], errors='coerce')
    
    tempo_aprovacao = (pedidos['order_approved_at'] - pedidos['order_purchase_timestamp']).dt.total_seconds() / 3600
    tempo_despacho = (pedidos['order_delivered_carrier_date'] - pedidos['order_approved_at']).dt.days
    
    print("\n===== ANÁLISE DE GARGALOS OPERACIONAIS =====")
    print(f"Tempo médio de aprovação: {tempo_aprovacao.mean():.2f} horas")
    print(f"Tempo médio de despacho: {tempo_despacho.mean():.2f} dias")

def analisar_retencao_atraso(base):
    logger.info("Analisando impacto do atraso na retenção de clientes...")
    contagem_compras = base.groupby('id_cliente_unico').size()
    clientes_recorrentes = contagem_compras[contagem_compras > 1].index
    primeira_compra = base.sort_values('data_compra').groupby('id_cliente_unico').first().reset_index()
    
    retorno_atraso = primeira_compra.groupby('atrasado')['id_cliente_unico'].apply(
        lambda ids: (ids.isin(clientes_recorrentes).mean() * 100)
    )
    print("\n===== ANÁLISE DE RETENÇÃO VS ATRASO =====")
    print(f"Taxa de retorno (Sem atraso na 1ª compra): {retorno_atraso[False]:.2f}%")
    print(f"Taxa de retorno (Com atraso na 1ª compra): {retorno_atraso[True]:.2f}%")

# =====================================================
# PIPELINE PRINCIPAL
# =====================================================
def main():
    try:
        logger.info("=== INICIANDO PIPELINE DE ANÁLISE LOGÍSTICA ===")
        
        # 1. Carga e Tratamento
        clientes, pedidos, itens = carregar_dados()
        clientes = tratar_clientes(clientes)
        pedidos_tratados = tratar_pedidos(pedidos)
        itens = tratar_itens(itens)

        # 2. Construção da Base
        base = criar_base(clientes, pedidos_tratados)
        base = criar_features(base)
        base = adicionar_receita_pedido(base, itens)

        # 3. Análises e KPIs
        outliers = detectar_outliers(itens)
        base['outlier'] = base['id_pedido'].isin(outliers['id_pedido'].unique())
        
        analisar_outliers_logistica(base, outliers)
        impacto_financeiro_atrasos(base)
        atraso_por_estado(base)
        impacto_financeiro_por_estado(base)
        ticket_medio_por_status(base)
        analisar_sazonalidade(base)
        analisar_gargalos(pedidos)
        analisar_retencao_atraso(base)

        # 4. Geração de Gráficos
        logger.info("Iniciando geração de gráficos para o portfólio...")
        os.makedirs('graficos', exist_ok=True)
        grafico_taxa_atraso_estado(base)
        grafico_receita_impactada(base)
        grafico_outlier_vs_normal(base)
        grafico_distribuicao_preco(itens)
        grafico_receita_total_vs_atraso(base)
        grafico_ticket_medio(base)
        grafico_sazonalidade(base)
        grafico_gargalos(pedidos)
        
        logger.info("=== PIPELINE FINALIZADO COM SUCESSO ===")
        
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante a execução: {str(e)}")

if __name__ == "__main__":
    main()
