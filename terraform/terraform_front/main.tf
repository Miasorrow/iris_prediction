# main.tf

resource "azurerm_linux_web_app" "iris_front_terraform" {
  name                = "irisfrontterraform"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_service_plan.irisManon.location
  service_plan_id     = data.azurerm_service_plan.irisManon.id

  app_settings = {
    WEBSITES_PORT = "8501"  # 👈 ton port ici
    API_URL = "https://${data.azurerm_linux_web_app.iris_back_terraform.default_hostname}"
  }

  site_config {
    application_stack {
      docker_image_name   = "miasorrow/iris_front:latest"
      docker_registry_url = "https://index.docker.io"
    }
  }
}

