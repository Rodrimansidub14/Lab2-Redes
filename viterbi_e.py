import socket
import random
import sys
import time

def texto_a_binario(texto):
    """Convierte un string en su representación binaria."""
    return ''.join(f"{ord(c):08b}" for c in texto)

def codificador_convolucional(in_bits):
    bits = [int(b) for b in in_bits]
    print(f"[DEBUG] Longitud de bits originales: {len(bits)}")
    bits += [0, 0]
    print(f"[DEBUG] Longitud después de flush: {len(bits)}")
    G1 = [1, 1, 1]
    G2 = [1, 0, 1]
    reg = [0, 0, 0]
    out = []
    for bit in bits:
        reg = reg[1:] + [bit]
        out1 = (reg[0] & G1[0]) ^ (reg[1] & G1[1]) ^ (reg[2] & G1[2])
        out2 = (reg[0] & G2[0]) ^ (reg[1] & G2[1]) ^ (reg[2] & G2[2])
        out.extend([out1, out2])
    print(f"[DEBUG] Longitud de mensaje codificado: {len(out)}")
    return ''.join(str(b) for b in out)

def aplicar_ruido(bits, error_rate=0.01):
    """Aplica ruido a la cadena de bits con una probabilidad dada."""
    return ''.join(
        str(int(b) ^ (random.random() < error_rate))
        for b in bits
    )

def enviar_con_retry(mensaje, puerto=46000, max_reintentos=10, espera=0.5):
    for intento in range(max_reintentos):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', puerto))
                s.sendall(mensaje.encode())
            print("Mensaje enviado al receptor por socket en puerto", puerto)
            return True
        except ConnectionRefusedError:
            print(f"Intento {intento+1}/{max_reintentos}: Receptor no disponible, reintentando...")
            time.sleep(espera)
    print("No se pudo conectar al receptor después de varios intentos.")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        mensaje = sys.argv[1]
        error_rate = float(sys.argv[2])
    else:
        mensaje = input("Ingrese el mensaje a codificar (puede ser texto o binario): ")
        error_rate = float(input("Tasa de error (ej. 0.01): "))

    print(f"[DEBUG] Mensaje recibido: {mensaje}")
    print(f"[DEBUG] Tasa de error: {error_rate}")

    if all(c in '01' for c in mensaje) and len(mensaje) % 8 == 0:
        bits = mensaje
        print("[DEBUG] Entrada detectada como binaria.")
    else:
        bits = texto_a_binario(mensaje)
        print(f"[DEBUG] Mensaje en binario: {bits}")

    codificado = codificador_convolucional(bits)
    print(f"[DEBUG] Mensaje codificado: {codificado}")

    con_ruido = aplicar_ruido(codificado, error_rate=error_rate)
    print(f"[DEBUG] Mensaje con ruido: {con_ruido}")

    print("[DEBUG] Intentando conectar al receptor...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 46000))
        print("[DEBUG] Conectado, enviando mensaje...")
        s.sendall(con_ruido.encode())
    print("Mensaje enviado al receptor por socket en puerto 46000.")