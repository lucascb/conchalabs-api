resource "google_vpc_access_connector" "vpc_connector" {
  name = "conchalabs-vpc-connector"
  subnet {
    name = google_compute_subnetwork.vpc_subnet.name
  }
  machine_type  = "e2-standard-4"
  min_instances = 2
  max_instances = 3
  region        = var.region
}

resource "google_compute_subnetwork" "vpc_subnet" {
  name          = "conchalabs-vpc-subnet"
  ip_cidr_range = "10.2.0.0/28"
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_compute_network" "vpc" {
  name                    = "conchalabs-vpc"
  auto_create_subnetworks = false
}