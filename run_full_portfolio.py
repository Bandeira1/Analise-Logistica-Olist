import os
import sys

# Criar pasta de gráficos
os.makedirs('graficos', exist_ok=True)

# Executar o script principal e capturar saída
print("Iniciando execução do pipeline...")
import analise_logistica_usuario
analise_logistica_usuario.main()

print("\nVerificando arquivos gerados:")
files = os.listdir('graficos')
for f in files:
    print(f"- {f}")

print(f"\nTotal de gráficos: {len(files)}")
