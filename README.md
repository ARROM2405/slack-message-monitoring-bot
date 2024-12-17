# Slack messagge monitoring bot

## Features
 * Monitoring of the messages and files posted in the Slack chat.
 * Keeping data validation patterns.
 * Removing messages validating data patterns and informing users in the chat about the removal.

## Running the project
1. Create and add to the chat slack app and provide permissions (maybe not all are needed):
   *  Bot Token Scopes
       * channels:history
       * channels:read
       * chat:write
       * chat:write.public
       * files:read
       * incoming-webhook
   * User Token Scopes
     * channels:history
     * chat:write
2. Add  `.env` file to the root directory of the project with the keys and added values below:
   * DJANGO:
     * `SECRET_KEY`
   * MYSQL:
     * `MYSQL_DATABASE`
     * `MYSQL_USER`
     * `MYSQL_PASSWORD`
     * `MYSQL_ROOT_PASSWORD`
     * `MYSQL_HOST`
     * `MYSQL_PORT`
   * SLACK:
     * `USER_TOKEN`
     * `BOT_TOKEN`
     * `DELETE_MESSAGE_URL`
     * `POST_MESSAGE_URL`
   * REDIS:
     * `REDIS_HOST`
     * `REDIS_HOST`
   * AWS:
     * `AWS_ACCESS_KEY_ID`
     * `AWS_SECRET_ACCESS_KEY`
     * `AWS_DEFAULT_REGION`
     * `MESSAGE_CHECK_QUEUE_URL`
     * `NEW_PATTERNS_QUEUE_URL`
   * Tool -> Django app connection:
     * `DATA_LOSS_POSITIVE_MESSAGES_ENDPOINT`
3. `docker compose -f docker/docker-compose.yml up --build -d django tool
`
## Implementation
There are 4 containers running:
1. Django app - receives all the events (posted messages) from the slack api. 
Checks if the event is a posted message - saves it to Redis and sends to the tool via SQS
for verification. 
All validation patterns manipulations are sent to the tool as well via signals.
2. Tool - container with data loss prevention tool, that receives user messages from django app
and runs validation versus all saved patterns. Tool receives information on all patterns manipulations.
Keeps information on patterns as a dict. That is being intentionally done, so database io operations are minimised.
3. Redis - is used to keep information about user messages. Only if the message fails validation, it is being saved to
database. Used for database operations optimization.
4. MYSQL - database.

## Possible enhancements
1. Add logging.
2. Add test db settings, so tests do not create objects on the real db.
