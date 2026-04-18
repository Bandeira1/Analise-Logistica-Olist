import pandas as pd
import os

# =====================================================
# CARGA DOS DADOS
# =====================================================

path = 'Banco/'

clientes = pd.read_csv(f'{path}olist_customers_dataset.csv')
pedidos  = pd.read_csv(f'{path}olist_orders_dataset.csv')
itens    = pd.read_csv(f'{path}olist_order_items_dataset.csv')

# =====================================================
# TRATAMENTO
# =====================================================

clientes = clientes.rename(columns={
    'customer_id':           'id_cliente',
    'customer_unique_id':    'id_cliente_unico',
    'customer_state':        'estado'
})

pedidos = pedidos.rename(columns={
    'order_id':                       'id_pedido',
    'customer_id':                    'id_cliente',
    'order_purchase_timestamp':       'data_compra',
    'order_delivered_customer_date':  'data_entregue_cliente',
    'order_estimated_delivery_date':  'data_estimada_entrega',
    'order_approved_at':              'data_aprovacao',
    'order_delivered_carrier_date':   'data_carrier'
})

for col in ['data_compra', 'data_entregue_cliente', 'data_estimada_entrega', 'data_aprovacao', 'data_carrier']:
    pedidos[col] = pd.to_datetime(pedidos[col], errors='coerce')

itens = itens.rename(columns={
    'order_id': 'id_pedido',
    'price':    'preco',
    'freight_value': 'frete'
})

# =====================================================
# BASE ANALÍTICA
# =====================================================

base = pedidos.merge(clientes[['id_cliente', 'id_cliente_unico', 'estado']], on='id_cliente', how='left')
base = base[base['order_status'] == 'delivered'].copy()

base['atrasado'] = base['data_entregue_cliente'] > base['data_estimada_entrega']

receita = itens.groupby('id_pedido')[['preco', 'frete']].sum()
receita['receita_total'] = receita['preco'] + receita['frete']
base = base.merge(receita[['receita_total']], on='id_pedido', how='left')

# =====================================================
# EXPORTAÇÕES
# =====================================================

os.makedirs('Banco/looker', exist_ok=True)

# 1. Donut — no prazo vs. atrasado
donut = pd.DataFrame({
    'Status':     ['No prazo', 'Atrasado'],
    'Percentual': [
        round((~base['atrasado']).mean() * 100, 2),
        round(base['atrasado'].mean() * 100, 2)
    ]
})
donut.to_csv('Banco/looker/donut_prazo.csv', index=False)
print("✓ donut_prazo.csv")

# 2. Ticket médio — no prazo vs. atrasado
ticket = (
    base.groupby('atrasado')['receita_total']
    .mean()
    .reset_index()
)
ticket['Status'] = ticket['atrasado'].map({True: 'Atrasado', False: 'No prazo'})
ticket = ticket[['Status', 'receita_total']].rename(columns={'receita_total': 'Ticket_Medio'})
ticket['Ticket_Medio'] = ticket['Ticket_Medio'].round(2)
ticket.to_csv('Banco/looker/ticket_medio.csv', index=False)
print("✓ ticket_medio.csv")

# 3. Retenção — taxa de retorno com/sem atraso na 1ª compra
contagem   = base.groupby('id_cliente_unico').size()
recorrentes = contagem[contagem > 1].index
primeira   = base.sort_values('data_compra').groupby('id_cliente_unico').first().reset_index()
retencao   = primeira.groupby('atrasado')['id_cliente_unico'].apply(
    lambda ids: round(ids.isin(recorrentes).mean() * 100, 2)
).reset_index()
retencao.columns = ['atrasado', 'Taxa_Retorno_Pct']
retencao['Status'] = retencao['atrasado'].map({
    True:  'Com atraso na 1ª compra',
    False: 'Sem atraso na 1ª compra'
})
retencao[['Status', 'Taxa_Retorno_Pct']].to_csv('Banco/looker/retencao.csv', index=False)
print("✓ retencao.csv")

# 4. Receita impactada por estado
receita_estado = (
    base[base['atrasado'] == True]
    .groupby('estado')['receita_total']
    .sum()
    .reset_index()
    .sort_values('receita_total', ascending=False)
    .head(10)
    .rename(columns={'receita_total': 'Receita_Impactada'})
)
receita_estado['Receita_Impactada'] = receita_estado['Receita_Impactada'].round(2)
receita_estado.to_csv('Banco/looker/receita_por_estado.csv', index=False)
print("✓ receita_por_estado.csv")

print("\nTodos os arquivos gerados em Banco/looker/")