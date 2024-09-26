# Description
This is a simple FastAPI application that provides API to work with molecules.

# Application stack
The application is dockerized and contains the following components:
- Two web containers with FastAPI application instances
- SQLAlchemy package to work with DB in OOP-style
- A container with PostreSQL DB to store molecule data
- Alembic package to maintain DB migrations
- A container to launch DB migrations prior to the web apps launch
- Celery worker container to handle long-running processes
- Redis container as message queue for Celery and as caching backend for the web app
- Nginx container to balance the web apps load

# CI/CD
The project contains GitHub actions with these steps:

## Tests and checks
flake8 checks are executed. 

There should also be test launches, but they were broken while migrating to Postgres, thus they are disabled at the moment.

## Deployment

The application is deployed on EC2 instance using the `ssh-action` action via SSH. 

SSH key was created, its private part was saved in GitHub secrets under the SSH_KEY variable, and its public part was added to the `authorized_keys` file on the EC2 instance.

Other secret variables are SSH_HOST which is the EC2 instance public IP address, and SSH_USERNAME which is `ubuntu`.

Script includes the following steps:
- removing of project's folder on the instance
- cloning of the project's repo working branch into the EC2 instance using HTTPS
- switching to the cloned folder
- building and running docker containers
