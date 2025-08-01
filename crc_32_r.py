import socket

POLY = 0xEDB88320

def crc32_bitwise(data_bytes):
    crc = 0xFFFFFFFF
    for byte in data_bytes:
        current_byte = byte
        for _ in range(8):
            bit = (crc ^ current_byte) & 1
            crc >>= 1
            if bit:
                crc ^= POLY
            current_byte >>= 1
    return crc ^ 0xFFFFFFFF

def binstr_to_bytes(binstr):
    bits = [c for c in binstr if c in '01']
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        while len(byte) < 8:
            byte.append('0')
        bytes_list.append(int(''.join(byte), 2))
    return bytes(bytes_list)

def bytes_to_binstr(data_bytes, original_length):
    bin_full = ''.join(f"{byte:08b}" for byte in data_bytes)
    return bin_full[:original_length]

def verify_crc(complete_message_bin):
    if len(complete_message_bin) <= 32:
        print("El mensaje es demasiado corto para contener CRC-32")
        return

    data_bin = complete_message_bin[:-32]
    recieved_crc_bin = complete_message_bin[-32:]
    recieved_crc = int(recieved_crc_bin, 2)

    data_bytes = binstr_to_bytes(data_bin)

    crc_calc = crc32_bitwise(data_bytes)

    print(f"El mensaje recibido fue: {complete_message_bin}")

    if recieved_crc == crc_calc:
        original_message = bytes_to_binstr(data_bytes, len(data_bin))
        print("No se detectaron errores en el mensaje")
        print(f"El mensaje original es: {original_message}")
    else:
        print("Se detectaron errores en el mensaje recibido. Se descartara el mensaje")

def recibir_mensaje_socket(puerto=45000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', puerto))
        s.listen(1)
        print(f"Esperando mensaje en puerto {puerto} ...")
        conn, addr = s.accept()
        with conn:
            print(f"Conexión desde {addr}")
            data = b''
            while True:
                chunk = conn.recv(2048)
                if not chunk:
                    break
                data += chunk
            mensaje = data.decode().strip()
            print("Mensaje recibido:", mensaje)
            return mensaje

if __name__ == "__main__":
    mensaje = recibir_mensaje_socket(45000)
    verify_crc(mensaje)