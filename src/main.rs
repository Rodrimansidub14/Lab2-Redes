use std::io;

const POLY: u32 = 0xEDB88320;

fn binary_string_to_bytes(s: &str) -> Vec<u8> {
    let bits: Vec<char> = s.chars().filter(|c| *c == '0' || *c == '1').collect();
    let mut bytes = vec![];

    for chunk in bits.chunks(8) {
        let mut byte = 0u8;
        for (i, bit) in chunk.iter().enumerate() {
            if *bit == '1' {
                byte |= 1 << (7 - i);
            }
        }
        bytes.push(byte);
    }

    bytes
}

fn crc32_bitwise(data: &[u8]) -> u32 {
    let mut crc = 0xFFFFFFFF;

    for &byte in data {
        let mut current_byte = byte;
        for _ in 0..8 {
            let bit = (crc ^ (current_byte as u32)) & 1;
            crc >>= 1;
            if bit != 0 {
                crc ^= POLY;
            }
            current_byte >>= 1;
        }
    }

    !crc
}

fn bytes_to_binary_string(bytes: &[u8]) -> String {
    bytes
        .iter()
        .map(|b| format!("{:08b}", b))
        .collect::<Vec<_>>()
        .join("")
}

fn main() {
    let mut input = String::new();
    println!("Ingresa un numero binario:");
    io::stdin().read_line(&mut input).expect("Fallo al leer entrada");

    let input = input.trim();
    let data = binary_string_to_bytes(input);

    if data.is_empty() {
        println!("Datos no validos");
        return;
    }

    let checksum = crc32_bitwise(&data);
    let crc_bin = format!("{:032b}", checksum);
    let original_bin = bytes_to_binary_string(&data);
    let final_message = format!("{}{}", original_bin, crc_bin);

    println!("El resultado del algoritmo es: {}", crc_bin);
    println!("El mensaje a enviar es: {}", final_message);
}
