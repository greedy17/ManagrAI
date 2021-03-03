# Set Up and Use the Managr Slack Integration

Set ngrok to the current request_url at:

    https://api.slack.com/apps/A01ERE1QAE9/interactive-messages

Feel free to change it as necessary.

    ngrok http -subdomain=managr-request-endpoint 8000

Set the following variables in the .env file:

    SLACK_CLIENT_ID=3505648522.1501477826485
    SLACK_SECRET= __

## Important Notes

Rotating/expiring Slack access tokens has not been implemented.
  - https://api.slack.com/legacy/workspace-apps/rotating-and-refreshing-credentials

Validating an incoming webhook is from Slack is not currently working.
  - See: `managr.slack.helpers.utils`

Endpoint for getting the Slack URL for a message is not implemented.
  - managr.slack.constants.CHAT_GET_PERMALINK
  - can leverage managr.slack.helpers.requests

## Reason for `l`, `o`, and `u` being single-character params

The reason the `l` , `o` , and `u` params are single-character params instead of more descriptively named is due to: `managr.slack.utils.action_with_params` .

There are three “types” of payloads supported by Slack that we are currently using. These are:

- `block_actions` - sent when user interacts with the UI (e.g. button) in a Slack Message.

- `block_suggestion` - sent when Slack wants to populate certain data in the UI of a Slack Message, and we are to provide this data.

- `view_submission` - sent when a user has hit a “submit” button on a modal.

When it comes to `block_actions` and `block_suggestion` payloads, the payload should include information on the piece of UI that is the target of the request from Slack:

- `block_actions` - the piece of UI the user just interacted with should be identifiable

- `block_suggestion` - the piece of UI that needs to be populated with our own data needs to be identifiable

The identifier for a UI element is a custom `action_id` we provide in each “block”.

In order to solve the following problem, I leveraged the `action_id` field to not only include an “id” (e.g. `GET_USER_LEADS` ) but also query params for this action that allows us to keep a context. Example problem:

- UI has a dropdown for “Change Opportunity” so that the user can change the opportunity associated with the ZoomMeeting, if we guessed wrong.

- This dropdown needs data from out server.

- Cool! So Slack will send us a request of type `block_suggestion` to populate the dropdown with whatever we send back.

- We give this dropdown an `action_id` of `GET_USER_LEADS` so that we know that this dropdown is to be populated with leads.

- But wait! Which user’s leads? So instead the action_id is `GET_USER_LEADS?u=<user UUID here>` , allowing context.

The param names are single-character because `action_id` are limited to 255 characters, so I am saving some string real estate in case we ever need a more complex “query string”.

## "State" in Slack Requests

When it comes to Slack allowing us “context”, you would think they would let us pass around a `state` object with everything we do, so that I did not need to turn `action_id` into a `GET request` look-alike query-string.

This is the case with modals, which are their API’s newer feature. Regular messages do not have `state`. The property is actually `private_metadata`.

So, since we receive a request of type `view_submission` on modal-submit, we do get to have context/state with `view_submission` requests (that is, Slack asks us to process the submission however we want).

But since `block_action`s and `block_suggestion` requests are not modal submissions, they do not have this `private_metadata` field, and do not have an equivalent either, as far as my research led me to conclude.

Hence `action_with_params`, a utils method (`managr.slack.helpers.utils`) that yields `action_id` + query string, letting us add `state`/context to these requests.
