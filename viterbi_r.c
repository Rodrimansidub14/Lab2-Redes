#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define K 3
#define NUM_STATES (1 << (K - 1))

int G1[] = {1, 1, 1};
int G2[] = {1, 0, 1};

typedef struct {
    int path[1024];
    int metric;
} State;

int hamming_distance(int a, int b) {
    int dist = 0;
    while (a || b) {
        if ((a & 1) != (b & 1)) dist++;
        a >>= 1;
        b >>= 1;
    }
    return dist;
}

int encode_output(int state, int input_bit, int *out1, int *out2) {
    int reg[K];
    reg[0] = input_bit;
    reg[1] = (state >> 1) & 1;
    reg[2] = state & 1;

        // Calcula salidas para cada generador
    *out1 = (reg[0] & G1[0]) ^ (reg[1] & G1[1]) ^ (reg[2] & G1[2]);
    *out2 = (reg[0] & G2[0]) ^ (reg[1] & G2[1]) ^ (reg[2] & G2[2]);
    return 0;
}

void viterbi_decode(const char *input, int length, int *decoded_bits) {
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
                    // Estado siguiente
                    int next_state = ((s << 1) | input_bit) & (NUM_STATES - 1);
                    // Calcula la salida esperada
                    int out1, out2;
                    encode_output(s, input_bit, &out1, &out2);
                    // Salida recibida en este paso
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

    for (int i = 0; i < num_steps - (K - 1); i++)
        decoded_bits[i] = states[best_state].path[i];
    printf("Métrica de error total: %d\n", best_metric);
}

int main() {
    char input[2048];
    printf("Ingrese la secuencia binaria codificada (ej: 011001...): ");
    scanf("%s", input);

    int length = strlen(input);
    if (length % 2 != 0) {
        printf("Error: longitud no válida\n");
        return 1;
    }
    int num_decoded = length / 2 - (K - 1);
    int decoded_bits[1024] = {0};
    viterbi_decode(input, length, decoded_bits);

    printf("Bits decodificados: ");
    for (int i = 0; i < num_decoded; i++)
        printf("%d", decoded_bits[i]);
    printf("\n");

    return 0;
}
