# biomrktools-web

### Run in localhost

- Create a virtual environment if it does not exist
> py -3.12 -m venv .venv

. Activate de virtual environment
> .\.venv\Scripts\Activate.ps1

- Install dependencies
> pip install -r requirements.txt


## Building the docker container

## Test the containerized app in localhost
> docker compose build --no-cache
>
> docker composer down
>
> docker composer up

## Publishing the Docker Image in Docker Hub
> docker login

> docker build -t biomrktools-web:latest .

- Create an image:
> docker build -t rodrisv/biomrktools-web:latest .

- Add a tag to the image (optional)
> docker tag rodrisv/biomrktools-web:latest biomrktools-web:latest

- Push to docker hub like this
> docker push rodrisv/biomrktools-web:latest

### Deplyo to Azure Container Apps

- Create a container revision:
  - Add the environment variables. T
  - The docker hub repository is being currently accessed trough a username: rodrisv and a password <password>. The storage account sas token should also be added as an environment variable for the container.
  - Enable ingress networks from anywhere (temp)
  - Give minumal pcu and storage settings.

- When you deploy to Azure Container Apps, you should not use admin creds. Instead, assign the AcrPull role to the Container App’s managed identity so it can pull the image cleanly.
