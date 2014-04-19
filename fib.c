// See https://gmplib.org/manual/Fibonacci-Numbers-Algorithm.html
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

int main(int argc, char *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <number>\n", argv[0]);
        return -1;
    }

    // get n from first cli argument
    long n = atol(argv[1]);

    if (n < 0) {
        fprintf(stderr, "Error calculating Fibonacci(%ld)\n", n);
        return -2;
    }

    // get n-th fibonacci number
    mpz_t f_n;
    mpz_init(f_n);
    mpz_fib_ui(f_n, n);

    // write it to stdout
    gmp_printf("fibonacci(%ld) = %Zd\n", n, f_n);

    // clean up and reclaim memory
    mpz_clear(f_n);

    return 0;
}

