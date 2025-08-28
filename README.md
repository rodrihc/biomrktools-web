# biomrktools-web

- Create a virtual environment if it does not exist
> PS:biomrktools-web> py -3.12 -m venv .venv

. Activate de virtual environment
> PS:biomrktools-web> .\.venv\Scripts\Activate.ps1

- Install dependencies
> PS:biomrktools-web> pip install -r requirements.txt


## Building the docker container

## Test the containerized app in localhost
> docker compose build --no-cache
>
> docker composer down
>
> docker composer up

## Publishing the Docker Image in Docker Hub
> docker build -t biomrktools-web:latest .

- Create an image:
> docker build -t rodrisv/biomrktools-web:latest .

- Add a tag to the image (optional)
> docker tag rodrisv/biomrktools-web:latest biomrktools-web:latest

- Push to docker hub like this
> docker push rodrisv/biomrktools-web:latest

### Later (for Azure Container Apps)

- When you deploy to Azure Container Apps, you should not use admin creds. Instead, assign the AcrPull role to the Container App’s managed identity so it can pull the image cleanly.
