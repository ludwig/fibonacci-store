
CC = clang
CFLAGS = -Wall
LDFLAGS = -lgmp

default:
	@echo Use tab completion on 'make' to see all available targets

fib: fib.c
	$(CC) -o $@ $(CFLAGS) $^ $(LDFLAGS)

BrowserNotifier: BrowserNotifier.go
	go build $^

start-notifier: BrowserNotifier
	./BrowserNotifier

start-redis:
	redis-server ./redis.conf

stop-redis:
	redis-cli shutdown save

start-celery-worker:
	celery worker -A tasks --loglevel=info

start-celery-multi:
	celery multi start 2 -A tasks -l info -Q:1 celery -c:1 2 -Q:2 arithmetic -c:2 1

stop-celery-multi:
	celery multi stop 2 -A tasks -l info

start-nginx:
	nginx -t -c ./nginx.conf -g "pid nginx.pid; worker_processes 2"

stop-nginx:
	nginx -s stop

requirements.txt:
	pip freeze > requirements.txt

start-flask:
	python ./fibserve.py

start-sass-watch:
	sass --watch static/css:static/css

clean:
	rm -f BrowserNotifier
	rm -f fib
	rm -f celery*.log

.PHONY: clean requirements.txt
