# biomrktools-web


- PS C:\biomarkers\repositories\biomrktools-web> py -3.12 -m venv .venv
- PS C:\biomarkers\repositories\biomrktools-web> .\.venv\Scripts\Activate.ps1
- pip install -r requirements.txt
- docker build -t biomrktools-web:latest .


### Create an image like this:
>docker build -t rodrisv/biomrktools-web:latest . 

### (Optional) add a tag to the image like this:
> docker tag rodrisv/biomrktools-web:latest biomrktools-web:latest

### push to docker hub like this
> docker push rodrisv/biomrktools-web:latest

### Later (for Azure Container Apps)

- When you deploy to Azure Container Apps, you should not use admin creds. Instead, assign the AcrPull role to the Container App’s managed identity so it can pull the image cleanly.
