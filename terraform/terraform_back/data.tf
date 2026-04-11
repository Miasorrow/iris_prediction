#data.tf

data "azurerm_resource_group" "rg" {
  name = var.rg_name
}

data "azurerm_service_plan" "irisManon" {
  name                = "irisManon"
  resource_group_name = data.azurerm_resource_group.rg.name
}
