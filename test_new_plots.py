import pandas as pd
from visualizacao import grafico_sazonalidade, grafico_gargalos
import os

# Criar pasta se não existir
os.makedirs('graficos', exist_ok=True)

# Carregar dados
clientes = pd.read_csv('/home/ubuntu/upload/olist_customers_dataset.csv')
pedidos = pd.read_csv('/home/ubuntu/upload/olist_orders_dataset.csv')

# Preparar dados mínimos
pedidos['order_purchase_timestamp'] = pd.to_datetime(pedidos['order_purchase_timestamp'])
pedidos['order_delivered_customer_date'] = pd.to_datetime(pedidos['order_delivered_customer_date'])
pedidos['order_estimated_delivery_date'] = pd.to_datetime(pedidos['order_estimated_delivery_date'])
pedidos['atrasado'] = pedidos['order_delivered_customer_date'] > pedidos['order_estimated_delivery_date']
pedidos['data_compra'] = pedidos['order_purchase_timestamp']

print("Gerando novos gráficos...")
grafico_sazonalidade(pedidos)
grafico_gargalos(pedidos)
print("Concluído.")
