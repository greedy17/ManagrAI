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


## Staging Environment

Our Staging Environment is hosted on heroku, the app name is Managr Staging 2, merging to develop should kick off the automatic deployment to staging. 
*Note the managr app can be accessed from `https://staging-2.managr.ai` it can also be accessed from `https://managr-staging-2.herokuapp.com`  PLEASE ONLY USE THE `managr.ai` endpoint as our redirects for the integrations redirect to that url. 

`heroku logs --tail --app managr-staging-2`

***!!!!! NOTE CURRENTLY THE APP WILL NOT AUTO DEPLOY BECAUSE TESTS ARE FAILING !!!!***

To deploy the app manually 

`git push <heroku-remote-name> branch:master`

*remember to run any migrations*

Most of the integrations will not work outside of the managr org when using staging, staging should be used more to assist Mike in debugging when he is demoing. See the below section on logs for information on logging with papertrail. 

## Prod Environment 

Prod is built on AWS, we have to ec2 instances running. One instance is a t2.micro, this one only serves the app. The other instance is a t2.medium this also serves the app but also runs cron jobs (it has a larger memory and is an 8 core). Note that in order to serve the asgi app both run a process for handling incoming asgi requests. We use sticky sessions to distribute traffic between the app, which instance the user is on depends on this and is cleared every 24hrs. When ether instance is unhealthy traffic is directed to the other instance (currently both fail health checks due to improper nginx setup). The RDS is served by AWS on its own instance as well. 

To SSH into the instance you must first set up your ssh access:


1. first login to the console (you should have your own credentials, reach out to William if not).
2. Navigate to the [instances page](https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Home:)
3. On the side bar select [security groups](https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#SecurityGroups:) (both share the same sg)
4. Select the correct [instance  id: sg-0d14e11db1aa9ec1c	label: production_ec2](https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#SecurityGroup:groupId=sg-0d14e11db1aa9ec1c)
5. Select Edit *Inbound Rules* and then *Add Rule*
6. In the type dropdown select *ssh*
7. In the source fropdown select *My Ip* and then *save rules*

On your computer you can now add your identity file:

1. open or create a config file (note this is for ease of access) `code ~/.ssh/config` or `vim ~/.ssh/config`
2. Paste the details for the two instances 

```
      Host *
      UseKeychain yes
      AddKeysToAgent yes

      Host AWS-Managr
      HostName 3.228.14.6
      user ubuntu 
      IdentityFile ~/.ssh/mgr_prod.pem

      Host AWS-Managr-2
      HostName 3.234.251.11
      user ubuntu
      IdentityFile ~/.ssh/mgr_prod.pem
```
3. Copy the pem file to your ssh directory this file can be found in [1 password](https://start.1password.com/open/i?a=QDUDXTQK4ZAJRBIRDQLLXXIMGE&v=y46ltqijnoyhqahtqhm5lb7jba&i=s4y3wu6qtpn3vakac3f7qtbjmi&h=aspire.1password.com) 
   
    `sudo echo -e <"PEM-FILE-DATE"> >> ~/.ssh/mgr_prod.pem` or `code ~/.ssh/mgr_prod.pem` 
   
   and paste data

5. chmod 400 my-key-pair.pem
6. to ssh `ssh AWS-Managr` or `ssh AWS-Managr-2` (2 is the t2.medium) 
  *you may be prompted about saving the fingerprint which you can do*
7. Activate the environment - `source /opt/venv/bin/activate`
8. cd into the managr directory - `cd managr`

Releasing to production 

When releasing to production we currently follow a manual process.
For BACKEND CODE ONLY:

1. Merge from develop to master
2. ssh into both instances
3. Activate the environment - `source /opt/venv/bin/activate`
4. cd into the managr directory - `cd managr`
5. pull master - `git pull master`
6. Run any migrations 
7. restart task nunners with `sudo supervisorctl restart all`

for FRONTEND w or w/o backend

1. Merge into develop 
2. checkout new branch with deploy keyword `git checkout -b deploy/<name>`
3. Remove old dist files in client folder 
4. ***Make sure you are using node 14.15.4 as is on prod*** `cd client && npm run build`
5. add newly built files to branch, commit and make a PR into develop
6. Merge deploy branch into develop
7. Merge develop into master
8. ssh into both instances
9. Activate the environment - `source /opt/venv/bin/activate`
10. cd into the managr directory - `cd managr`
11. pull master - `git pull master`
12. Collect static files `server/manage.py collectstatic --noinput`
13. Run any migrations `server/manage.py migrate`
14. restart task nunners with `sudo supervisorctl restart all`
   

## Logs

### Papertrail logs 
We use [papertrail](https://papertrailapp.com/dashboard) to aggregate logs, this makes them easier to search. Some common search terms that may be helpful are program:<log> to show only data in the process_tasks.log, see bellow for the different log options. 

[Staging PaperTrail Group](https://my.papertrailapp.com/groups/23969332/events)
[Prod PaperTrail Group](https://my.papertrailapp.com/groups/23950522/events)

### Viewing on the server

Both instances have logs located in main managr directory `managr/logs` directory. Both will have the `asgi.log` which is the main directory for incoming requests. The logs for any of the async tasks will be found in `logs/process_tasks.log` which are all handled by the `AWS-Managr-2` instance (the t2.medium), there are also the nginx logs that record incoming requests before they are channeled to the `asgi.log`

See all data in log file

`cat logs/<log-file>.log`

Tail only last 100 lines 

`tail logs/<log-file>.log`



### Async Logs
Data from bg tasks are recorded in the process_tasks.log:
1. SFSyncOperation - syncs all sf data
2. SFFieldSync - syncs all sf object fields 
3. MeetingWorkflow - the async meeting workflow tasks 

*Note when creating a new resource for a meeting we use sync functions that are logged in both instance `asgi.logs`*

*Note when updating a resource from a command we use sync functions that are logged in both instance `asgi.logs`*

Cron jobs are handled by supervisor, you can see the cron jobs by running 

`crontab -l`

you can edit cron jobs by running 

`crontab -e`



### Adding new variables to the terraform configuration 

1. 
   1. ***Sensitive*** in **ecs.tf** add variable to **aws_secretsmanager_secret_version** this will add the variable to the secrets managr
   2. ***Insensitive*** in **ecs.tf** add variable to the **template_file** since it can be exposed 
2. Add the variable in the **variables.tf** to **environments**
3. Add the variable in the **managr_app.json.tpl** and the **managr_app_tasks.json.tpl** file since we have multiple task definitions here add the variable to the ones that it needs (eg. app and tasks)
4. add to **Dockerfile** for each environment (if needed)
5. add to **default.auto.tfvars** for deployment 
6. Run `terraform apply -auto-approve -parallelism=1` to apply changes 

### SSH Into (New) Environments 

Install [session manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-macos) if you have not already done so 



`aws ecs execute-command --cluster managr-cluster --task <task_id> --container <container_name> --interactive --command "/bin/bash"`

You can get the correct task_id by looking at the AWS Console under ECS tasks there may be multiple definitions running (if there was autoscaling) any one will do, the container_name corresponds to the container you are accessing aka managr-app, managr-tasks etc. 

### Describe the task definition

`aws ecs execute-command --cluster managr-cluster --task <task_id> --container <container_name> --interactive --command "/bin/bash"`


### One time code to add new public fields to user's forms 


    form_templates=OrgCustomSlackForm.objects.filter()
    for template in form_templates:
      ## check to see if the form already has duplicates before adding 
      exists = template.formfield_set.filter(field_id="fae88a10-53cc-470e-86ec-32376c041893").exists()
      if not exists:
        FormField.objects.create(form=template, order=0, field=SObjectField.objects.get(id="fae88a10-53cc-470e-86ec-32376c041893"))
      exists = template.formfield_set.filter(field_id="e286d1d5-5447-47e6-ad55-5f54fdd2b00d").exists()
      if not exists:
        FormField.objects.create(form=template, order=0, field=SObjectField.objects.get(id="e286d1d5-5447-47e6-ad55-5f54fdd2b00d"))

