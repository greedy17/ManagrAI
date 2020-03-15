# ThinkNimble New App Bootstrapper

## Bootstrapper To-Dos and Wishlist

William, 2019-11-25: I've copied in the following from our #bootstrapper channel. We can check in on these in a future dev process meeting. In the meantime

Things to finish on the Bootstrapper:
 - Implement Channels
 - Remove Bulma
 - Remove irrelevant stuff from package.json
 - Remove irrelevant stuff from client/tests
 - Add new code to utils?
 - Deploy and test
 - (Neil, 2019-10-17) Add pagination service to client/services/utils folder

      See: https://bitbucket.org/thinknimble/tn-components/src/master/vue/services/pagination.js

      William, 2019-11-25: We've recently taken this a bit further and created a `CollectionManager` class. It would be good to include this in the bootstrapper and provide some documentation and examples for how to use it.

Future:
- IN PROGRESS: Build “mobile” folder for mobile apps?
- Build separate “users” Django app?
- Build an automated tool to set up a new environment for new users

****

## New App Checklist

**In the Root Directory**

1. Edit 'Procfile': replace `templateapp.wsgi` with `{your_app_name}.wsgi`.
2. Update the name of application in package.json and package-lock.json

**In the Server Directory (/server)**

1. Change name of templateapp to the name of the new application
2. Change `templateapp.settings` to `{your_app_name}.settings` in line 10 of manage.py

**In the Django app directory (/server/{new_app_name})**

1. Replace every instance of `templateapp` in settings.py
2. Replace `templateapp.settings` in line 18 of wsgi.py
3. Replace `template.core.urls` in templateapp/urls.py
4. Replace `templateapp.core` in INSTALLED_APPS in templateapp/settings.py

**Server Config Directory (/server/config)**

1. Copy .env.example to root directory (`cp /server/config/.env.example .env`). More on configuring this below.


## TODO: Instructions on how to upgrade to Django Channels

## TODO: Revise the following

----------------

**Generate favicons**

The Django app is already configured to serve favorite icons for all browsers and platforms (include, for example, apple-icons and android-icons at various sizes). By default, this icon is the 'Aspire flame' logo.

Visit [favicon-generator.org](https://www.favicon-generator.org/) and upload a high resolution, square version of the image you would like to use as the favicon for this app.

Download the ZIP file of icons that the site generates for you and paste them in the `client/static/favicons/` directory (yes, it is OK to overwrite the default 'Aspire flame' icons in that directory).

_Optional: Change theme color_ - Find the `<meta name="theme-color"...` tag in `client/src/index.html` and change the value of `content` to the HEX code of the color you want. The default color is 'Aspire Red' (HEX code `#d73126`).


**Configure Your .env File**

A .env file is required for development, but no configuration should be required to get your app up and running. When you are ready to test and prototype third-party services like AWS and Mailgun, the following may be helpful:

 - Set up an AWS Access Key ID if you'd like to use AWS. If you aren't using it, set `USE_AWS_STORAGE` to 'False'
 - Create a Mailgun Account and set the Mailgun API Key to that API key. If you aren't using it, leave it blank.
 - Create a Rollbar app in the shared Rollbar account and get the server access token from the dashboard. Set `ROLLBAR_ACCESS_TOKEN` to this value
