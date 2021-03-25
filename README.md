# Managr App #

**All Passwords and secrets can be found in 1password**

## To Get Up and Running ##

First, see the section below on setting up your .env files, the proceed with installing system dependencies. 

### With Virtual Environments ###

[Follow the instructions in the ThinkNimble developer setup guide.](https://docs.google.com/document/d/1nRLCNbfoknrcb762cwgjSChzsbkTzr1MH4AyLgRLKQc/edit)

[Note if you get a pillow error the fix is easy using this](https://aspireperks.atlassian.net/wiki/spaces/TNWIKI/pages/486932532/Developer+Setup+Guide#For-Django-developers%3A)

This app depends on:
 - PostgreSQL 12
 - Python 3.7 + pipenv - The Pipfile in the root directory defines the Python dependencies
   - It is recommended to use pyenv to install and manage Python version
 - Node 12 - package.json in the root directory and client/package.json outline these dependencies
   - It is recommended to use Node Version Manager (NVM) to install and manage Node versions

### Or, use Docker ###

This project contains configuration for running the client, server, and postgres inside of containers. These configs are very much in a "beta" stage. The necessary Docker and Docker Compose commands are organized in a Makefile for convenience and documentation purposes.

To start a dev environment with Docker:

1. [Download and install Docker for your system](https://docs.docker.com/get-docker/)
2. Add `export DOCKER_UID=$(id -u):$(id -g)` to your bash profile*
3. `make build` - Will run the docker-compose command to build your containers.
4. Make sure your database host is set to 'postgres', and not 'localhost' in you server/.env file
5. `make run` - Will begin running the containers

Access the backend at localhost:8000 and the front end dev server at localhost:8080 as usual.

*This makes it so that any files or folders created within the container are owned by your user. This is an awkward workaround, and we are looking for a better solution. If you access the shell of your containers, it will say "I have no name!" instead of your username, but it does work.

## How to Configure Your .env Files ##

The client and server each have their own .env files. `.env.example` files are provided that should be ready to go. Make copies of them like so:

```bash
cp client/.env.example client/.env.local
cp server/.env.example server/.env
```

Not that the client .env file has a special extension based on the environment name.

A .env file is required for development, but no configuration should be required to get your app up and running. When you are ready to test and prototype third-party services like AWS and Mailgun, the following may be helpful:

 - Set up an AWS Access Key ID if you'd like to use AWS. If you aren't using it, set `USE_AWS_STORAGE` to 'False'
 - Create a Mailgun Account and set the Mailgun API Key to that API key. If you aren't using it, leave it blank.
 - Create a Rollbar app in the shared Rollbar account and get the server access token from the dashboard. Set `ROLLBAR_ACCESS_TOKEN` to this value

## Load Data for Local Development ##

Some data has been prepared as a fixture. Run the following to load it into your local database.

```bash
./server/manage.py loaddata fixture.json
```

## How to Generate favicons ##

The Django app is already configured to serve favorite icons for all browsers and platforms (include, for example, apple-icons and android-icons at various sizes). By default, this icon is the 'Aspire flame' logo.

Visit [favicon-generator.org](https://www.favicon-generator.org/) and upload a high resolution, square version of the image you would like to use as the favicon for this app.

Download the ZIP file of icons that the site generates for you and paste them in the `client/static/favicons/` directory (yes, it is OK to overwrite the default 'Aspire flame' icons in that directory).

_Optional: Change theme color_ - Find the `<meta name="theme-color"...` tag in `client/src/index.html` and change the value of `content` to the HEX code of the color you want. The default color is 'Aspire Red' (HEX code `#d73126`).


## Preparing your local environment

After following the developer guide and creating your database you are ready to get started with your local environment. 

Here are the steps to get you started:

1. Set up ngrok (see below for instructions)
2. Run your initial migrations `server/manage.py migrate`
3. Create a super user `server/manage.py createsuperuser`
4. Run your frontend and backend servers `server/manage.py runserver` & `npm run serve`
5. Run the task processor `server/manage.py process_tasks`
6. To refresh data every 5 mins (resource data) and 12 hours (object fields) run the cron jobs *(Only run this once and then end the cron job otherwise you will use up all the licenses we all share)*
7. Create a new user through the user registration screen (remember you will need the code)
8. Integrate Salesforce, zoom, slack and nylas
9. Create your first zoom meeting and invite a user *(note we will use this meeting as your fake testable meeting in the future see below)*
    


### Setting up ngrok

We use ngrok to direct traffic to localhost when developing locally, a number of our integrations do not allow redirects to localhost directly. 

*Please Note Only One user can be using ngrok forwarded to the same subdomain at a time*

1. Download the [zip file](https://ngrok.com/download) 
2. Unzip and copy to home directory 
3. Install your authoken with this command: `ngrok authtoken <YOUR_AUTHTOKEN>`
   
`~/ngrok http [port]`

If you have added your token you can initiate ngrok to a subdomain (note that ngrok is added to the list of allowed hosts in our settings.py)

`~/ngrok http 8000 --subdomain thinknimble`

*Please Note Only One user can be using ngrok forwarded to the same subdomain at a time*

## Staging Environment

## Prod Environment 
