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
