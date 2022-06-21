# Birthday reminder

## Video Demo: https://www.youtube.com/watch?v=_YgHf4D31kQ&t=4s

## Description:

Birthday Reminder is a web application written in Python and Flask.
Add birthdays of friends and family members easily and get email reminders automatically.

Until now, the birthdays of my friends and family were recorded in my personal
calendar. The problem was that I could not set reminders as I wanted and that my
calendar was overfilled by these entries. Therefore, I wanted to write an
application that would take care of the birthdays specifically and send me
corresponding early reminders.

From the technology side, I was interested in trying Python and Flask as an
alternative to Javascript and Node.js. I also wanted to use Docker for the first
time for my own project.

The original plan was to host the Docker containers on Amazon. During the
development I decided to rather install it locally on my Raspberry Pi. This gave
me the opportunity to get to know Ubuntu Server for the first time.

The project itself contains the following main files:

- `app.py`: Main project source code
- `database.py`: Setup of the database using the mysql-connector library
- `helpers.py`: Helpers functions
- `scheduler.py`: Setup of the background scheduler using the apscheduler library

In the templates folder you find all the html templates.
In the static folder you find the favicon, the main logo of the applications and
the css styles.

Important: To make the application work, you have to create an `app.env` and
`database.env` file in the root folder.

The `app.env` file must define the following configuration values:

```
BR_FLASK_ENV = 'development'
BR_SESSION_TYPE = 'filesystem'
BR_SESSION_PERMANENT = False
BR_MAIL_SUBJECT = 'Birthday Reminder'
BR_MAIL_SERVER = 'smtp.gmail.com'
BR_MAIL_PORT = 465
BR_MAIL_USE_SSL = True
BR_MAIL_USERNAME = 'email.from.which.the.reminders.are.sent@gmail.com'
BR_MAIL_PASSWORD = 'password'
```

The `database.env` file must define the following configuration value:

```
MYSQL_ROOT_PASSWORD = 'password'
```

# Notes

## Docker

https://docs.docker.com

### Build image

The command `docker build` builds Docker images from a Dockerfile and a "context".

The build command optionally takes a `--tag` flag, which is used to set the name
of the image. If you also want to set a tag simply use `name:tag`.

Example 1 (Build Docker image only with tag flag):

```
docker build --tag <IMAGE_NAME> .
```

Example 2 (Build Docker image with name and tag):

```
docker build --tag <IMAGE_NAME>:<IMAGE_TAG> .
```

With `docker images` you can view local images.

Create a new tag for a local image:

```
docker tag <IMAGE_NAME>:latest <IMAGE_NAME>:v1.0.0
```

The tag points to the same image and is just another way to reference the image.

Remove tag:

```
docker rmi <IMAGE_NAME>:v1.0.0
```

### Run containers

A container is a normal operating system process except that this process is
isolated in that it has its own file system, its own networking, and its own
isolated process tree separate from the host.

Run image inside of a container:

```
docker run -p 8000:5000 <IMAGE_NAME>
```

`-p` for short means `--publish`, which is important to set. We need to publish
a port for our container. The format is: `[host port]:[container port]`.
So in the upper example we expose port 5000 inside the container to port 8000
outside of the container.

Now you can connect to the application via:

```
localhost:8000
```

If you start a web server, you don't have to be connected to the container. In this
case you can run the container in detached mode (in the backround) as follows:

```
docker run -d -p 8000:5000 <IMAGE_NAME>
```

`-d` for short means `--detach`.

To name the container simple use the --name flag as follows:

```
docker run -d -p 8000:5000 --name <CONTAINER_NAME> <IMAGE_NAME>
```

With `docker ps` you can view local running containers.
With `docker ps --all` or `docker ps -a` you can view local containers.
With `docker stop <CONTAINER_ID>` or `docker stop <CONTAINER_NAME>` you can stop a running container.
With `docker rm <CONTAINER_ID>` or `docker rm <CONTAINER_NAME>` you can remove a container.

### Create volumes

Simply use the following command to create a new volume:

```
docker volume create <VOLUME_NAME>
```

### Create network

If you want that your application and database can talk to each other, you need
to create a network.

Simply use the following command to create a new network:

```
docker network create <NETWORK_NAME>
```

### Run MySQL in a container and attach to the volumes and network

Since you only have the volume and not the image itself, Docker will pull the image
from Hub and run it locally for you.

```
docker run --rm -d \
-v mysql:/var/lib/mysql \
-v mysql_config:/etc/mysql \
-p 3306:3306 \
--network mysqlnet \
--name mysqldb \
-e MYSQL_ROOT_PASSWORD=p@ssw0rd1 \
<IMAGE_NAME>
```

<IMAGE_NAME> = mysql

To connect to the MySQL interactive terminal use the following command:

```
docker exec -ti mysqldb mysql -u root -p
```

If successfully connected navigate to database as follows:

```
USE datbase_name;
```

### Add application container to the database network and run it

This allows us to access the database by its container name.

```
docker run \
--rm -d \
--network mysqlnet \
--name rest-server \
-p 8000:5000 \
<IMAGE_NAME>
```

If you do not want to pass all the parameters to the docker run command, you can
use a Compose file: For example `docker-compose.dev.yml`.

After setting up a Compose file, you can simply run the following command:

```
docker-compose -f docker-compose.yml up --build
```

## Python

### Interactive Python interpreter

> Type `python3` in the terminal to start the prompt of the interactive Python interpreter

### VS Code Setup

- Select a Python interpreter (lower left)
- Run `*.py` file with start button top right
- F5 to start debugger

### Virtual environment and package installation

- Create and activate the virtual environment:
  - Create: `python3 -m venv .venv`
  - Activate: `source .venv/bin/activate`
- Select your new environment by using the Python: Select Interpreter command from the Command Palette.
- Install packages: `python3 -m pip install <PACKAGE_NAME>`
- Use `pip list` to check which package are installed including information about the version
- Once you are finished, type `deactivate` in the terminal window to deactivate the virtual environment.
