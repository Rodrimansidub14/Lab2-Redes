import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("graphs", exist_ok=True)

df = pd.read_csv("resultados_crc.csv")

color_ok = "#219a52"
color_err = "#e81d1d"

conteo = df["resultado"].value_counts()[["ok", "error"]]

plt.figure(figsize=(7,5))  # Más ancho
bars = plt.bar(conteo.index, conteo.values, color=["#219a52", "#e81d1d"], width=0.6, edgecolor="black")

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 100, f"{int(yval)}", ha='center', va='bottom', fontsize=9, fontweight="bold")

plt.title("Mensajes correctos vs incorrectos (CRC)", fontsize=17)
plt.ylabel("Cantidad", fontsize=12)
plt.xlabel("Resultado", fontsize=12)
plt.xticks(fontsize=5)
plt.yticks(fontsize=5)
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("graphs/conteo_ok_vs_error_crc.png")
plt.show()


pivot_error = df.groupby("error_rate")["resultado"].value_counts(normalize=True).unstack().fillna(0)
pivot_error = pivot_error[["ok", "error"]] if "ok" in pivot_error.columns and "error" in pivot_error.columns else pivot_error
pivot_error.plot(kind='bar', stacked=True, color=[color_ok, color_err], figsize=(7,4))
plt.title("Proporción OK/Error por tasa ")
plt.ylabel("Proporción")
plt.xlabel("Tasa de error")
plt.legend(["OK", "Error"], title="Resultado")
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("graphs/ok_error_by_errorrate.png")
plt.close()

ok_table = df[df["resultado"]=="ok"].groupby(["tam_msg", "error_rate"]).size().unstack().fillna(0)
total_table = df.groupby(["tam_msg", "error_rate"]).size().unstack().fillna(0)
prop_table = (ok_table/total_table).fillna(0)
plt.figure(figsize=(8,4))
import seaborn as sns
sns.heatmap(prop_table, annot=True, fmt=".2f", cmap="Greens", cbar_kws={'label': 'Proporción de mensajes OK'})
plt.title("mensajes OK por tamaño y tasa")
plt.ylabel("Tamaño del mensaje")
plt.xlabel("Tasa de error")
plt.tight_layout()
plt.savefig("graphs/ok_by_size_and_errorrate.png")
plt.close()

print("¡Gráficas mejoradas guardadas en la carpeta 'graphs'! 🚀")
