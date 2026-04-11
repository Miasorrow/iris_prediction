#var.tf

variable "rg_name" {
  description = "The name of the resource group in which to create the virtual network and subnet."
  type        = string
}

variable "ClientId" {
  description = "The Client ID of the Azure AD application used for authentication."
  type        = string
}

variable "ClientSecret" {
  description = "The Client Secret of the Azure AD application used for authentication."
  type        = string
  sensitive   = true
}

variable "TenantId" {
  description = "The Tenant ID of the Azure AD application used for authentication."
  type        = string
}

variable "SubscriptionId" {
  description = "The Subscription ID of the Azure account used for authentication."
  type        = string
}