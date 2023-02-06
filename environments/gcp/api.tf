resource "google_cloud_run_v2_service" "api_service" {
  name     = "conchalabs-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 2
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.instance.connection_name]
      }
    }

    containers {
      image = var.app_image

      env {
        name  = "DATABASE_URL"
        value = "postgresql+asyncpg://${var.database_user}:${var.database_password}@${google_sql_database_instance.instance.private_ip_address}:5432/${var.database_name}"
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      startup_probe {
        failure_threshold     = 5
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 3

        http_get {
          path = "/health"
          http_headers {
            name  = "Access-Control-Allow-Origin"
            value = "*"
          }
        }
      }

      liveness_probe {
        failure_threshold     = 5
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 3

        http_get {
          path = "/health"
          http_headers {
            name  = "Access-Control-Allow-Origin"
            value = "*"
          }
        }
      }
    }

    vpc_access {
      connector = google_vpc_access_connector.vpc_connector.id
      egress    = "ALL_TRAFFIC"
    }

    annotations = {
      "run.googleapis.com/client-name"        = "terraform"
      "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.instance.connection_name
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_service_iam_binding" "api_service_iam" {
  location = google_cloud_run_v2_service.api_service.location
  service  = google_cloud_run_v2_service.api_service.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}
