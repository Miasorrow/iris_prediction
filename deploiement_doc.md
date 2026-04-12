## Déploiement d'une application sur Azure

Nous allons déployé une application sur azure une application simple : un back et un front
Pour cela nous avons besoin de 2 conteneurs. Les deux conteneur ont besoin d'une image docker la pour celle ci python des fichiers du front et du back et des commandes pour exécuter le code et des ports à exposer.
Cette méthode se fait dans une Dockerfile : 

Voici le docker file du back

```Dockerfile
FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY src .
EXPOSE 8000

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"] 
```
Et celui du front

```dockerfile
FROM python:3.12

WORKDIR /app

RUN pip install streamlit 

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

On peut facilement tester ça en local en faisant un build et un run des 2 conteneurs grâce à Docker

```bash
docker build --tag iris_back
sudo docker run iris_back -p 8000:8000
```


```bash
sudo docker build -f Dockerfile --tag iris_front
sudo docker run -p 8501:8501 iris_front
 ```

Maintenant l'idée est de faire la même chose mais sur Azure

Pour build l'image nous allons utiliser Dockerhub 
Ma première méthode est de faire en 2 étapes une première étape de github vers DockerHub puis de Dockerhub vers Azure
J'ai donc fait un pipeline sur github

```yml
name: Build & Push Docker images

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build & push API image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/iris_prediciton:latest
        
      
      - name: Build & push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./front
          file: ./front/Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/iris_prediciton_front:latest
```
Une fois sur docker hub je crée mes webapp sur Azure et je les lie les webapp à mes images de dockers hub

Par la suite pour rendre ça plus automatique j'ai fait un pipeline sur github qui réunis les 2 Le build de l'image dans dockerhub et le déploiement dans les webapp que j'ai aussi crée a la main

```yml
name: Build & Push Docker images

on:
  push:
    branches:
      - main

jobs:
  build-and-push:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build & push API image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/iris_prediciton:latest
        
      
      - name: Build & push Frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./front
          file: ./front/Dockerfile
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/iris_prediciton_front:latest

```

Pour une automatisation complète des tâches ci dessus j'ai décidé d'utiliser terraform
Terraform est un outil d'automatisation et la il me permettra de créer aussi les webapp qu'on crée sur azure directement mais cette fois ci avec terraform

Pour tester terraform je commence par déployer un subnet ça me permet de comprendre cet outil

La config de provider me permet de me connecter à azure 
Ses variables de connexion on doit les récupérer dans azure en créant une app registration
La on les met en dur mais par la suite je les mettrais dans un var.tf 

```hcl

#providers.tf

# We strongly recommend using the required_providers block to set the
# Azure Provider source and version being used
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}

  client_id       = "XXXXX"
  client_secret   = "XXXXXX"
  tenant_id       = "XXXXXX"
  subscription_id = "XXXXXXX"
}
```
Le main c'est la ou déclare les ressources à créer

```tf
# main.tf



resource "azurerm_virtual_network" "manon_network" {
  name                = "manon-vnet" #nom du subnet
  address_space       = ["10.0.0.0/16"]
  location            = data.azurerm_resource_group.rg.location # comme quand on choisis la région d'un webservice
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "manon_subnet" {
  name                 = "manon-subnet"
  resource_group_name  = azurerm_virtual_network.manon_network.resource_group_name
  virtual_network_name = azurerm_virtual_network.manon_network.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "delegation"

    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action"]
    }
  }
}

Le var permet de déclarer les variables attendu par terraform

```py
#var.tf

variable "rg_name" {
  description = "The name of the resource group in which to create the virtual network and subnet."
  type        = string
}
```

Le data.tf permet de récupérer les infos de ressources azure qui existe déjà comme la location ou le nom de mon ressource_group 

```tf
#data.tf

data "azurerm_resource_group" "rg" {
  name = var.rg_name
}

```

Les commandes pour lancer terraform que je mettrais par la suite dans mon pipeline sur github sont

```bash
terraform init
terraform plan
terraform apply
terraform destroy
```
Mais comme on a fait des variables il attend aussi les variables dans la commande

```bash
terraform apply -var rg_name=manon
``` 



Maintenant j'ai fait la meme chose pour mon application

Dans data j'ai récupéré le infos des ressources qui existent déjà


Dans var.tf j'ai variabiliser les secrets pour éviter qu'ils soient visibles


La voici la ressource crée dans le main : 

```ty
# main.tf
resource "azurerm_linux_web_app" "iris_back_terraform" {
  name                = "irisbackterraform"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_service_plan.irisManon.location
  service_plan_id     = data.azurerm_service_plan.irisManon.id

  app_settings = {
    WEBSITES_PORT = "8000"  # 👈 ton port ici
  }

  site_config {
    application_stack {
      docker_image_name   = "miasorrow/iris_back:latest"
      docker_registry_url = "https://index.docker.io"
    }
  }
}
``` 

Et j'ai fait la meme chose dans le front

j'ai testé depuis mon ordinateur avec les commandes comme plus haut mais avec toutes les variables

exemple de la commande

```bash
terraform apply -var rg_name=manon -var ClientId=${{ secrets.AZURE_CLIENT_ID}} -var ClientSecret=${{ secrets.AZURE_SECRET_ID}} -var TenantId=${{ secrets.AZURE_TENANT_ID }} -var SubscriptionId=${{ secrets.AZURE_SUB_ID }}
```

Puis j'ai fait un pipeline qui automatise tout ça

Dockerhub puis terraform

```yml
name: Build, Push to DockerHub and Deploy to Azure Web App
env:
  DOCKERHUB_IMAGE_BACK: ${{ secrets.DOCKER_USERNAME }}/iris_back
  DOCKERHUB_IMAGE_FRONT: ${{ secrets.DOCKER_USERNAME }}/iris_front
  AZURE_WEBAPP_BACK: Irispredictionback2
  AZURE_WEBAPP_FRONT: irisfront2
on:
  push:
    branches: ["master"]
  workflow_dispatch:
permissions:
  contents: write
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'Dockerfile'
              - 'src/**'        # 👈 adapter selon ta structure
            frontend:
              - 'front/**'
              - 'front/Dockerfile'

  build-and-push-back:
    needs: detect-changes
    if: needs.detect-changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD}}
      - name: Build and push BACK to Docker Hub
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ${{ env.DOCKERHUB_IMAGE_BACK }}:${{ github.sha }}
            ${{ env.DOCKERHUB_IMAGE_BACK }}:latest
          file: ./Dockerfile   # 👈 adapter le chemin

  build-and-push-front:
    needs: detect-changes
    if: needs.detect-changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD}}
      - name: Build and push FRONT to Docker Hub
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ${{ env.DOCKERHUB_IMAGE_FRONT }}:${{ github.sha }}
            ${{ env.DOCKERHUB_IMAGE_FRONT }}:latest
          context: ./front
          file: ./front/Dockerfile   # 👈 adapter le chemin
  deploy-back:
    runs-on: ubuntu-latest
    needs: [build-and-push-back, build-and-push-front]
    if: always() && !failure() && !cancelled() && needs.build-and-push-back.result == 'success'
    environment:
      name: 'Development'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init
        working-directory: ./terraform/terraform_back  # 👈 adapter le chemin

      - name: Terraform Plan
        run: terraform plan -var rg_name=manon -var ClientId=${{ secrets.AZURE_CLIENT_ID}} -var ClientSecret=${{ secrets.AZURE_SECRET_ID}} -var TenantId=${{ secrets.AZURE_TENANT_ID }} -var SubscriptionId=${{ secrets.AZURE_SUB_ID }}
        working-directory: ./terraform/terraform_back

      - name: Terraform Apply 
        run: terraform apply -auto-approve -var rg_name=manon -var ClientId=${{ secrets.AZURE_CLIENT_ID}} -var ClientSecret=${{ secrets.AZURE_SECRET_ID}} -var TenantId=${{ secrets.AZURE_TENANT_ID }} -var SubscriptionId=${{ secrets.AZURE_SUB_ID }}
        working-directory: ./terraform/terraform_back
  deploy-front:
    runs-on: ubuntu-latest
    needs: [build-and-push-back, build-and-push-front]
    if: always() && !failure() && !cancelled() && needs.build-and-push-front.result == 'success'
    environment:
      name: 'Development'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init
        working-directory: ./terraform/terraform_front  # 👈 adapter le chemin

      - name: Terraform Plan
        run: terraform plan -var rg_name=manon -var ClientId=${{ secrets.AZURE_CLIENT_ID}} -var ClientSecret=${{ secrets.AZURE_SECRET_ID}} -var TenantId=${{ secrets.AZURE_TENANT_ID }} -var SubscriptionId=${{ secrets.AZURE_SUB_ID }}
        working-directory: ./terraform/terraform_front

      - name: Terraform Apply
        run: terraform apply -auto-approve -var rg_name=manon -var ClientId=${{ secrets.AZURE_CLIENT_ID}} -var ClientSecret=${{ secrets.AZURE_SECRET_ID}} -var TenantId=${{ secrets.AZURE_TENANT_ID }} -var SubscriptionId=${{ secrets.AZURE_SUB_ID }}
        working-directory: ./terraform/terraform_front
```