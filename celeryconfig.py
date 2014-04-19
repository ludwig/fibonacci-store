
# http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html#broker-redis
BROKER_URL = 'redis://localhost:6379/0'

# http://docs.celeryproject.org/en/latest/configuration.html#conf-redis-result-backend
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_RESULT_EXPIRES = 3600

# http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#configuration
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'America/Los_Angeles'
CELERY_ENABLE_UTC = True

# http://docs.celeryproject.org/en/latest/configuration.html#celery-queues
# http://docs.celeryproject.org/en/latest/userguide/routing.html#manual-routing
# http://stackoverflow.com/questions/5463241/celery-run-different-workers-on-one-server
CELERY_ROUTES = {
    'tasks.fib': {'queue': 'celery'},
    'tasks.add': {'queue': 'arithmetic'},
}

# EOF
