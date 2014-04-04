
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

