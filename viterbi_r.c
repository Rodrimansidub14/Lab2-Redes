#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

#define K 3
#define NUM_STATES (1 << (K - 1))
#define PORT 46000

int G1[] = {1, 1, 1};
int G2[] = {1, 0, 1};

typedef struct {
    int path[1024];
    int metric;
} State;

int encode_output(int state, int input_bit, int *out1, int *out2) {
    int reg[K];
    reg[0] = (state >> 1) & 1;    // MÁS ANTIGUO
    reg[1] = state & 1;           // INTERMEDIO
    reg[2] = input_bit;           // MÁS NUEVO (igual que emisor)
    *out1 = (reg[0] & G1[0]) ^ (reg[1] & G1[1]) ^ (reg[2] & G1[2]);
    *out2 = (reg[0] & G2[0]) ^ (reg[1] & G2[1]) ^ (reg[2] & G2[2]);
    return 0;
}

void viterbi_decode(const char *input, int length, int *decoded_bits, int *metric_out) {
    int num_steps = length / 2;
    State states[NUM_STATES], next_states[NUM_STATES];

    for (int s = 0; s < NUM_STATES; s++) {
        states[s].metric = (s == 0) ? 0 : 9999;
        memset(states[s].path, 0, sizeof(states[s].path));
    }

    for (int step = 0; step < num_steps; step++) {
        for (int s = 0; s < NUM_STATES; s++) next_states[s].metric = 9999;

        for (int s = 0; s < NUM_STATES; s++) {
            if (states[s].metric < 9000) {
                for (int input_bit = 0; input_bit <= 1; input_bit++) {
                    int next_state = ((s << 1) | input_bit) & (NUM_STATES - 1);
                    int out1, out2;
                    encode_output(s, input_bit, &out1, &out2);
                    int rx1 = input[2 * step]   - '0';
                    int rx2 = input[2 * step+1] - '0';
                    int hd = (out1 != rx1) + (out2 != rx2);

                    int metric = states[s].metric + hd;
                    if (metric < next_states[next_state].metric) {
                        next_states[next_state].metric = metric;
                        memcpy(next_states[next_state].path, states[s].path, sizeof(states[s].path));
                        next_states[next_state].path[step] = input_bit;
                    }
                }
            }
        }
        memcpy(states, next_states, sizeof(states));
    }

    int best_state = 0, best_metric = states[0].metric;
    for (int s = 1; s < NUM_STATES; s++) {
        if (states[s].metric < best_metric) {
            best_metric = states[s].metric;
            best_state = s;
        }
    }

    int num_decoded = num_steps - (K - 1);
    for (int i = 0; i < num_decoded; i++)
        decoded_bits[i] = states[best_state].path[i];

    *metric_out = best_metric;
}

void bits_a_texto_ascii(int *bits, int num_bits) {
    printf("Mensaje ASCII decodificado: ");
    int i = 0;
    for (; i + 7 < num_bits; i += 8) {
        int val = 0;
        for (int j = 0; j < 8; j++) {
            val = (val << 1) | bits[i + j];
        }
        printf("%c", val);
    }
    printf("\n");
}


int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char input[2048] = {0};

    printf("[DEBUG] Creando socket...\n");
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("[DEBUG] socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    printf("[DEBUG] Haciendo bind...\n");
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("[DEBUG] bind failed");
        exit(EXIT_FAILURE);
    }

    printf("[DEBUG] Escuchando en puerto %d...\n", PORT);
    if (listen(server_fd, 1) < 0) {
        perror("[DEBUG] listen");
        exit(EXIT_FAILURE);
    }

    printf("[DEBUG] Esperando conexión entrante...\n");
    if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
        perror("[DEBUG] accept");
        exit(EXIT_FAILURE);
    }
    printf("[DEBUG] Conexión aceptada.\n");

    int valread = read(new_socket, input, sizeof(input)-1);
    printf("[DEBUG] Bytes leídos: %d\n", valread);
    input[valread] = '\0';

    printf("[DEBUG] Mensaje recibido: %s\n", input);

    int length = strlen(input);
    printf("[DEBUG] Longitud de mensaje recibido: %d\n", length);
    if (length % 2 != 0) {
        printf("[DEBUG] Error: longitud no válida\n");
        return 1;
    }

    int num_steps = length / 2;
    int num_decoded = num_steps - (K - 1);
    int decoded_bits[1024] = {0};
    int metric = 0;
    printf("[DEBUG] Decodificando mensaje...\n");
    viterbi_decode(input, length, decoded_bits, &metric);

    printf("[DEBUG] Bits decodificados: ");
    for (int i = 0; i < num_decoded; i++)
        printf("%d", decoded_bits[i]);
    printf("\n");

    bits_a_texto_ascii(decoded_bits, num_decoded);

    if (metric == 0) {
        printf("Sin errores detectados.\n");
    } else if (metric == 1) {
        printf("Se detectó y corrigió 1 error en la transmisión.\n");
    } else {
        printf("Se detectaron y corrigieron %d errores, pero el mensaje puede estar corrupto si hay más de un error.\n", metric);
    }

    printf("[DEBUG] Cerrando sockets.\n");
    close(new_socket);
    close(server_fd);

    return 0;
}
