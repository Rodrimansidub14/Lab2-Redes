use std::io::{self, Write};
use std::net::TcpStream;
use rand::Rng;

const POLY: u32 = 0xEDB88320;
const DEST_ADDR: &str = "127.0.0.1:45000";

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

fn bytes_to_binary_string(bytes: &[u8]) -> String {
    bytes.iter()
        .map(|b| format!("{:08b}", b))
        .collect::<Vec<String>>()
        .join("")
}

fn crc32_bitwise(data: &[u8]) -> u32 {
    let mut crc = 0xFFFFFFFFu32;
    for &byte in data {
        crc ^= byte as u32;
        for _ in 0..8 {
            if crc & 1 != 0 {
                crc = (crc >> 1) ^ POLY;
            } else {
                crc >>= 1;
            }
        }
    }
    !crc
}

fn add_noise(message: &str, error_rate: f64) -> String {
    let mut rng = rand::thread_rng();
    message.chars()
        .map(|bit| {
            if rng.gen_bool(error_rate) {
                if bit == '0' { '1' } else { '0' }
            } else {
                bit
            }
        })
        .collect()
}

fn main() {
    let mut ascii_input = String::new();
    println!("Ingrese texto ASCII:");
    io::stdin()
        .read_line(&mut ascii_input)
        .expect("Error al leer entrada");
    let ascii_input = ascii_input.trim_end();

    let mut error_input = String::new();
    println!("Ingrese la probabilidad de error por bit (ej. 0.01 para 1%):");
    io::stdin()
        .read_line(&mut error_input)
        .expect("Error al leer probabilidad");
    let error_rate: f64 = error_input.trim().parse().unwrap_or(0.0);

    let binary_string = ascii_input
        .chars()
        .map(|c| format!("{:08b}", c as u8))
        .collect::<Vec<String>>()
        .join("");

    let data = binary_string_to_bytes(&binary_string);
    if data.is_empty() {
        println!("Datos no validos");
        return;
    }

    let checksum = crc32_bitwise(&data);
    let crc_bin = format!("{:032b}", checksum);
    let original_bin = bytes_to_binary_string(&data);
    let final_message = format!("{}{}", original_bin, crc_bin);

    println!("El mensaje recibido fue: {}", &ascii_input);
    println!("El mensaje en binario es: {}", &binary_string);

    println!("Mensaje antes del ruido: {}", final_message);

    let noisy_message = add_noise(&final_message, error_rate);

    println!("Mensaje después del ruido: {}", noisy_message);

    match TcpStream::connect(DEST_ADDR) {
        Ok(mut stream) => {
            stream.write_all(noisy_message.as_bytes())
                .expect("Error al enviar mensaje");
            println!("Mensaje enviado a {}", DEST_ADDR);
        }
        Err(e) => {
            eprintln!("Error al conectar a {}: {}", DEST_ADDR, e);
        }
    }
}