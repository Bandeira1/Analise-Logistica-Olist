import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def grafico_taxa_atraso_estado(df):
    atraso_estado = (
        df.groupby("estado")["atrasado"]
        .mean()
        .sort_values(ascending=False) * 100
    )
    plt.figure()
    sns.barplot(x=atraso_estado.values, y=atraso_estado.index)
    plt.title("Taxa de Atraso por Estado (%)")
    plt.xlabel("Taxa de Atraso (%)")
    plt.ylabel("Estado")
    plt.tight_layout()
    plt.savefig("graficos/taxa_atraso_estado.png")
    plt.close()

def grafico_receita_impactada(df):
    receita_estado = (
        df[df["atrasado"] == 1]
        .groupby("estado")["receita_total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    plt.figure()
    sns.barplot(x=receita_estado.values, y=receita_estado.index)
    plt.title("Top 10 Estados - Receita Impactada por Atraso")
    plt.xlabel("Receita Impactada")
    plt.ylabel("Estado")
    plt.tight_layout()
    plt.savefig("graficos/receita_impactada_estado.png")
    plt.close()

def grafico_outlier_vs_normal(df):
    comparacao = (df.groupby("outlier")["atrasado"].mean() * 100)
    labels = ["Normal", "Outlier"]
    plt.figure()
    plt.bar(labels, comparacao.values)
    plt.title("Taxa de Atraso: Outlier vs Normal")
    plt.ylabel("Taxa de Atraso (%)")
    plt.xlabel("Tipo de Pedido")
    plt.tight_layout()
    plt.savefig("graficos/outlier_vs_normal.png")
    plt.close()

def grafico_distribuicao_preco(df):
    plt.figure()
    sns.histplot(df["preco"], bins=50)
    plt.title("Distribuição de Preços")
    plt.xlabel("Preço")
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig("graficos/distribuicao_preco.png")
    plt.close()

def grafico_receita_total_vs_atraso(df):
    resumo = df.groupby("atrasado")["receita_total"].sum()
    labels = ["No Prazo", "Atrasado"]
    plt.figure()
    plt.bar(labels, resumo.values)
    plt.title("Receita Total vs Receita com Atraso")
    plt.ylabel("Receita Total")
    plt.xlabel("Status da Entrega")
    plt.tight_layout()
    plt.savefig("graficos/receita_total_vs_atraso.png")
    plt.close()

def grafico_ticket_medio(base):
    resumo = base.groupby('atrasado')['receita_total'].mean()
    labels = ["No Prazo", "Atrasado"]
    valores = [resumo[False], resumo[True]]
    plt.figure()
    plt.bar(labels, valores)
    plt.title("Comparação de Ticket Médio")
    plt.ylabel("Ticket Médio (R$)")
    plt.xlabel("Status da Entrega")
    for i, v in enumerate(valores):
        plt.text(i, v + 2, f"R$ {v:,.2f}", ha='center')
    plt.tight_layout()
    plt.savefig("graficos/ticket_medio_comparacao.png")
    plt.close()

def grafico_sazonalidade(base):
    plt.figure(figsize=(12, 6))
    base['mes_ano'] = base['data_compra'].dt.to_period('M')
    tendencia = base.groupby('mes_ano')['atrasado'].mean() * 100
    tendencia.plot(kind='line', marker='o', color='#dc2626', linewidth=2)
    plt.title("Tendência Mensal de Taxa de Atraso (%)", fontsize=14, fontweight='bold')
    plt.ylabel("Taxa de Atraso (%)")
    plt.xlabel("Mês de Compra")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig("graficos/sazonalidade_atraso.png")
    plt.close()

def grafico_gargalos(pedidos):
    plt.figure(figsize=(10, 6))
    t_aprov = (pd.to_datetime(pedidos['order_approved_at']) - pd.to_datetime(pedidos['order_purchase_timestamp'])).dt.total_seconds() / 3600
    t_desp = (pd.to_datetime(pedidos['order_delivered_carrier_date']) - pd.to_datetime(pedidos['order_approved_at'])).dt.days
    labels = ['Aprovação (Horas)', 'Despacho (Dias)']
    valores = [t_aprov.mean(), t_desp.mean()]
    plt.bar(labels, valores, color=['#3b82f6', '#f59e0b'])
    plt.title("Gargalos Operacionais Médios", fontsize=14, fontweight='bold')
    for i, v in enumerate(valores):
        plt.text(i, v + 0.1, f"{v:.2f}", ha='center', fontweight='bold')
    plt.tight_layout()
    print("Tentando salvar gargalos_operacionais.png...")
    plt.savefig("graficos/gargalos_operacionais.png")
    print("Salvo com sucesso.")
    plt.close()
