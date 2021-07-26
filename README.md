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


## How to Configure Your .env Files ##

***MOST ENV VARIABLES THAT ARE PRIVATE CAN BE FOUND IN 1Password Ensure you have access***
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



## Load Data ##

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
2. Add a .env.local file and point the backend to your local server `VUE_APP_DEV_SERVER_BACKEND="http://localhost:8000"`
3. Run your initial migrations `server/manage.py migrate`
4. Create a super user `server/manage.py createsuperuser`
5. Run your frontend and backend servers `server/manage.py runserver` & `npm run serve`
6. Run the task processor `server/manage.py process_tasks`
7. To refresh data every 10 mins (resource data) and 12 hours (object fields) run the cron jobs *(Only run this once and then end the cron job otherwise you will use up all the licenses we all share)*
8. Make sure to loadfixtures for custom fields `server/manage.py loaddata fixture`
9. Create a new user through the user registration screen (remember you will need the code)
10. Integrate Salesforce, zoom, slack and nylas
11. Create your first zoom meeting and invite a user *(note we will use this meeting as your fake testable meeting)*
12. Navigate to the admin pannel and find your meeting in the ZoomMeetings tab copy the unique id for this meeting 
13. In your environment variables (managr/server/.env) paste the meeting uuid in ZOOM_FAKE_MEETING_UUID
14. If you correctly followed the instructions for getting set up in the previous section then you have NVM it is best to switch to 14.15.4 when developing to match prod (since we build locally before deploying)

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

### Key Notes 
**server/manage.py process_tasks is responsible for grabbing all background tasks**
  
*If any code changes that is used by the task processor you need to restart it to use the updated code*

### Commands

`server/manage.py reinitsfsync <user email>`
- this will init a bg task to resync resource (saleslforce object rows)

  
`server/manage.py reinitsffieldsync <user email>`
- this will init a bg task to resync resource fields (saleslforce object fields)
  
`server/manage.py initresourcesync`
- this comand is an automated cron job in prod it initiates the sync for all users every 10 mins ***as long as their previous flow has reached 100%***

`server/manage.py initobjectfieldsync`
- this comand is an automated cron job in prod it initiates the sync for all users every 12 hours ***as long as their previous flow has reached 100%***

`server/manage.py manuallyrefreshsftoken <user email>`
- this comand can be used to manually refresh an sf token if for some reasone the while loop in functions cannot do it 

`server/manage.recreateslackforms <user email>`
- this comand can be used to manually recreate slack forms ***USE THIS COMMAND SPARINGLY AS IT WILL CLEAR ORG FORMS AND WILL BREAK THE REVIEW CONTACTS BUTTON FOR ALL EXISTING USER SLACKS THAT HAVE NOT BEEN COMPLETED SINCE THAT FORM SAVES DATA ON WORKFLOWS***

`server/manage.py sfsynclogs`
- this comand can will email a report (to whomever is the staff email in your .env) of a users resource sync flows we can use this to check on whether a user has failed their latest sync. If they have then the automated resync will not work 


## Environments

Prod is built on AWS, and is deployed using terraform as an orchestration, you can find the relevant informatin in the deploy/Readme.md



***Checkout the readme.md in the deploy directory for more information like how to connect, add variables and apply changes***

## Logs 


Currently logs are collected from each individual container they are set up using terraform in the logs.tf file. 
These are sent to CloudWatch and are maintained for 30 days before being deleted. Once in CloudWatch we pipe the logs to datadog where you can watch the logs in a tail form.
You can build different dashboards to match up to the logs in datadog with requests being made. 
To view the logs you can visitn this link [Logs](https://app.datadoghq.com/logs)




