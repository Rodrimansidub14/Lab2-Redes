# Laboratorio 2 - Esquemas de deteccion y correcion de errores

## Descripcion
Este laboratorio contiene implementaciones para algoritmos de deteccion y correcion de errores. Cada algoritmo tiene tiene una parte de emisor y otra de receptor, cada una de ellas escritas en lenguajes de programacion diferentes.

## Autores
- 22046 - Nelson Escalante
- 22611 - Rodrigo Mansilla

## Uso

### CRC-32
Para correr los archivos correspondientes a CRC-32 se debe hacer lo siguiente

#### Emisor
Compilar el archivo `main.rs` con Cargo

```bash
cargo build
```

Correr el archivo.

```bash
cargo run
```

El programa solicitara un numero en binario con una longitud maxima de 32 bits. Luego de recibir el numero, el programa imprimira en pantalla el mensaje final, listo para ser enviado.
