import pandas as pd
import matplotlib.pyplot as plt
import os
import re

csv_file = "resultados_convolucional.csv"
output_dir = "graphs"
os.makedirs(output_dir, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')

df = pd.read_csv(csv_file)

def extrae_num_errores(x):
    x = str(x).lower()
    match = re.search(r'(\d+)\s*errores* corregidos*', x)
    if match:
        return int(match.group(1))
    elif "error corregido" in x:
        return 1
    else:
        return 0

df['errores_corregidos'] = df['resultado'].apply(extrae_num_errores)

def parse_categoria(x):
    x = str(x).lower()
    if "sin errores" in x and "corregido" not in x:
        return "ok"
    elif "corrupto" in x:
        return "corrupto"
    elif "corregido" in x:
        return "corregido"
    else:
        return "otro"

df['categoria'] = df['resultado'].apply(parse_categoria)

plt.figure(figsize=(10,6))
colors = {"ok": "#27ae60", "corregido": "#2980b9", "corrupto": "#e74c3c"}
for cat in ["ok","corregido","corrupto"]:
    props = []
    for err in sorted(df["error_rate"].unique()):
        subset = df[df["error_rate"]==err]
        pct = (subset['categoria']==cat).mean()*100
        props.append(pct)
    plt.plot(sorted(df["error_rate"].unique()), props, marker="o", label=cat.capitalize(), color=colors[cat])
plt.xlabel("Tasa de error", fontsize=13)
plt.ylabel("% de mensajes", fontsize=13)
plt.title("Distribución de resultados por tasa de error (Convolucional)", fontsize=15)
plt.legend(title="Resultado", loc="upper right", fontsize=12, bbox_to_anchor=(1,1))
plt.tight_layout()
plt.savefig(f"{output_dir}/conv_resultados_vs_error_rate.png", dpi=200)
plt.close()

pivot = df.pivot_table(index="tam_msg", columns="error_rate", values="errores_corregidos", aggfunc="mean")
pivot.plot(kind="bar", figsize=(10,6), color=["#3498db", "#f39c12"])
plt.title("Promedio de errores corregidos por tamaño y tasa de error (Convolucional)", fontsize=15)
plt.ylabel("Errores corregidos (promedio)", fontsize=13)
plt.xlabel("Tamaño del mensaje", fontsize=13)
plt.legend(title="Tasa de error", fontsize=12)
plt.tight_layout()
plt.savefig(f"{output_dir}/conv_errores_corregidos.png", dpi=200)
plt.close()

propor_corrupto = df.groupby("tam_msg")["categoria"].apply(lambda x: (x=="corrupto").mean())
propor_corrupto.plot(kind="bar", color="#e67e22", figsize=(8,5), edgecolor='black')
plt.title("Proporción de mensajes corruptos por tamaño (Convolucional)", fontsize=15)
plt.ylabel("Proporción corruptos", fontsize=13)
plt.xlabel("Tamaño del mensaje", fontsize=13)
plt.tight_layout()
plt.savefig(f"{output_dir}/conv_prop_corruptos_tam.png", dpi=200)
plt.close()

propor_ok = df.groupby("tam_msg")["categoria"].apply(lambda x: (x=="ok").mean())
propor_ok.plot(kind="bar", color="#2ecc71", figsize=(8,5), edgecolor='black')
plt.title("Proporción de mensajes OK por tamaño (Convolucional)", fontsize=15)
plt.ylabel("Proporción OK", fontsize=13)
plt.xlabel("Tamaño del mensaje", fontsize=13)
plt.tight_layout()
plt.savefig(f"{output_dir}/conv_prop_ok_tam.png", dpi=200)
plt.close()

print("Gráficas guardadas en 'graphs/'")

print("\nTABLA RESUMEN POR TAMAÑO Y TASA DE ERROR (Convolucional):")
tabla = df.pivot_table(index="tam_msg", columns="error_rate", values="categoria", aggfunc=lambda x: (x=="ok").mean())
print((tabla*100).round(1), "\n")
