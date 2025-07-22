def texto_a_binario(texto):
    """
    Convierte un string en su representación binaria 
    """
    return ''.join(f"{ord(c):08b}" for c in texto)


def codificador_convolucional(in_bits):
    bits = [int(b) for b in in_bits]
    bits += [0, 0]
    
    G1 = [1, 1, 1]  
    G2 = [1, 0, 1]  
    
    reg = [0, 0, 0]  
    out = []
    
    for bit in bits:
        reg = [bit] + reg[:2]
        out1 = (reg[0] & G1[0]) ^ (reg[1] & G1[1]) ^ (reg[2] & G1[2])
        out2 = (reg[0] & G2[0]) ^ (reg[1] & G2[1]) ^ (reg[2] & G2[2])
        out.extend([out1, out2])
    
    return ''.join(str(b) for b in out)


if __name__ == "__main__":
    mensaje = input("Ingrese el mensaje a codificar (puede ser texto o binario): ")
    # Detectar si la entrada es binaria (solo 0s y 1s)
    if all(c in '01' for c in mensaje) and len(mensaje) % 8 == 0:
        bits = mensaje
        print("Entrada detectada como binaria.")
    else:
        bits = texto_a_binario(mensaje)
        print(f"Mensaje en binario: {bits}")
    codificado = codificador_convolucional(bits)
    print(f"Mensaje codificado: {codificado}")