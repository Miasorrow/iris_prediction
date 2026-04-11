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

  client_id       = var.ClientId
  client_secret   = var.ClientSecret
  tenant_id       = var.TenantId
  subscription_id = var.SubscriptionId
}