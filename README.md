# biomrktools-web


- PS C:\biomarkers\repositories\biomrktools-web> py -3.12 -m venv .venv
- PS C:\biomarkers\repositories\biomrktools-web> .\.venv\Scripts\Activate.ps1
- pip install -r requirements.txt
- docker build -t biomrktools-web:latest .
- docker tag biomrktools-web:latest biomrktools-hvbxcnd8d4a3ahg9.azurecr.io/biomrktools-web:latest
- docker login biomrktools-hvbxcnd8d4a3ahg9.azurecr.io -ubiomrktools -p <the-password>
- docker push biomrktools-hvbxcnd8d4a3ahg9.azurecr.io/biomrktools-web:latest

### Later (for Azure Container Apps)

- When you deploy to Azure Container Apps, you should not use admin creds. Instead, assign the AcrPull role to the Container App’s managed identity so it can pull the image cleanly.
