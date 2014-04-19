
# Goal

Serve fibonacci numbers to a user browsing a website, via a websocket notification.

# Data Flow

User requests a large fibonacci number from website.

Request for computation gets put into a celery task queue.

Once task finishes, notification daemon gets a message and forwards answer to the user.

If the user is still browsing the site and has an active websocket, a non-intrusive popup
should appear on the user's page.

If the user has no active connection, result gets saved to a redis database.
Upon the user's next visit, user will receive all outstanding notifications.

# JavaScript

The javascript libraries are installed using Bower.

It's configured using a file called `bower.json`. For the specific syntax, refer to
<https://github.com/bower/bower.json-spec>

Note that in `.bowerrc` we specify the directory where bower should install our specified
packages.  In this case, we choose to put everything in the `/static/bower_components` subdirectory
so that the flask dev server and nginx can find.

To install the specified javascript libraries

    bower install

To update the libraries

    bower update

# Flask

To start the flask server

    ./fibserve.py

# Redis

To start redis

    make start-redis

# Celery

To start celery

    make start-celery-multi

# BrowserNotifier

To start the browser notifier daemon,

    make BrowserNotifier && ./BrowserNotifier

# Calculating Fibonacci numbers with `fib`

To build the `fib` executable

    make fib

Now you can calculate fibonacci numbers by passing in a single cli argument.
For example,

    ./fib 100

<!-- EOF -->
