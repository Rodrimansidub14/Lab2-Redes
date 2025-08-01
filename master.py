import subprocess, random, string, time, csv

N_PRUEBAS = 1000
TAM_MSGS = [8, 16, 32]
ERROR_RATES = [0.01, 0.05]
STACKS = ["crc", "convolucional"]

print("¿Qué pruebas quieres ejecutar?")
print("1) Solo CRC")
print("2) Solo Convolucional")
print("3) Ambas (todas las pruebas)")
opcion = input("Selecciona una opción (1/2/3): ").strip()

if opcion == "1":
    selected_stacks = ["crc"]
elif opcion == "2":
    selected_stacks = ["convolucional"]
else:
    selected_stacks = STACKS

archivos = {
    "crc": "resultados_crc.csv",
    "convolucional": "resultados_convolucional.csv"
}

for stack in selected_stacks:
    with open(archivos[stack], "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["stack", "tam_msg", "error_rate", "prueba", "mensaje", "resultado"])
        for tam_msg in TAM_MSGS:
            for error_rate in ERROR_RATES:
                for i in range(N_PRUEBAS):
                    mensaje = ''.join(random.choices(string.ascii_letters + string.digits, k=tam_msg))
                    res = "desconocido"
                    try:
                        if stack == "crc":
                            receptor = subprocess.Popen(
                                ["python3", "crc_32_r.py"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            )
                            time.sleep(0.2)
                            emisor = subprocess.Popen(
                                ["./target/release/Lab2-Redes"],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                            )
                            emisor.stdin.write(f"{mensaje}\n{error_rate}\n")
                            emisor.stdin.flush(); emisor.stdin.close()
                            stdout, _ = receptor.communicate(timeout=3)
                            out = stdout.decode()
                            if "No se detectaron errores" in out:
                                res = "ok"
                            elif "Se detectaron errores" in out:
                                res = "error"
                        elif stack == "convolucional":
                            receptor = subprocess.Popen(
                                ["./viterbi"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            )
                            time.sleep(1)
                            emisor = subprocess.Popen(
                                ["python3", "emisor_convolucional.py", mensaje, str(error_rate)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            )
                            stdout, _ = receptor.communicate(timeout=3)
                            out = stdout.decode()
                            if "Sin errores detectados" in out:
                                res = "ok"
                            elif "corrigió" in out or "corrigieron" in out:
                                res = "corregido"
                            elif "puede estar corrupto" in out:
                                res = "corrupto"
                    except subprocess.TimeoutExpired:
                        receptor.kill()
                        res = "timeout"
                    writer.writerow([stack, tam_msg, error_rate, i+1, mensaje, res])
                    if (i+1) % 10 == 0:
                        print(f"{stack}, msg={tam_msg}, err={error_rate}: {i+1}/{N_PRUEBAS}")

print("Pruebas terminadas.")
for s in selected_stacks:
    print(f"Resultados de {s} guardados en: {archivos[s]}")
