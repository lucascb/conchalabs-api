resource "google_cloud_run_v2_job" "migration_job" {
  name         = "migration-job"
  location     = var.region
  launch_stage = "BETA"

  template {
    template{
      volumes {
        name = "cloudsql"
        cloud_sql_instance {
          instances = [google_sql_database_instance.instance.connection_name]
        }
      }

      containers {
        image = var.migration_image

        env {
          name  = "DATABASE_URL"
          value = "postgresql+asyncpg://${var.database_user}:${var.database_password}@${google_sql_database_instance.instance.private_ip_address}:5432/${var.database_name}"
        }

        volume_mounts {
          name = "cloudsql"
          mount_path = "/cloudsql"
        }
      }

      vpc_access {
          connector = google_vpc_access_connector.vpc_connector.id
          egress    = "ALL_TRAFFIC"
      }
    }
  }
}