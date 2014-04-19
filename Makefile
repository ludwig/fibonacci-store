
CC = clang
CFLAGS = -Wall
LDFLAGS = -lgmp

fib: fib.c
	$(CC) -o $@ $(CFLAGS) $^ $(LDFLAGS)

clean:
	rm -f fib

.PHONY: clean
