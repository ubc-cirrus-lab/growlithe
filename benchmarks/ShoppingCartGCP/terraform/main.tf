#
# Terraform Configuration
#

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.3.0"
    }
  }

  backend "gcs" {
    bucket = "data-terminus-393416-terraform-state-bucket"
    prefix = "terraform/state"
  }
}

provider "google" {
  project     = "data-terminus-393416"
  region      = "us-central1"
  credentials = "${path.module}/serviceAccountKey.json"
}

# Bucket where the Terraform state is stored:
resource "google_storage_bucket" "terraform-state" {
  name          = "data-terminus-393416-terraform-state-bucket"
  force_destroy = false
  location      = "us-central1"
  storage_class = "STANDARD"
  versioning {
    enabled = true
  }
  public_access_prevention = "enforced"
}

# Bucket where the source code is stored:
resource "google_storage_bucket" "source-code" {
  name          = "data-terminus-393416-source-code"
  location      = "us-central1"
  storage_class = "STANDARD"
  public_access_prevention = "enforced"
}


#
# AddToCart Function
#

resource "google_cloudfunctions_function" "add-to-cart" {
  name = "add-to-cart-function"
  runtime = "nodejs20"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.source-code.name
  source_archive_object = google_storage_bucket_object.add-to-cart-source-code.name
  trigger_http          = true
  entry_point           = "addToCart"
  min_instances = 1
  max_instances = 1
}

# Source code is stored at:
resource "google_storage_bucket_object" "add-to-cart-source-code" {
  name   = filesha256("./add_to_cart.zip")
  bucket = google_storage_bucket.source-code.name
  source = "./add_to_cart.zip"
}

# IAM permission for invoking the function
resource "google_cloudfunctions_function_iam_member" "add-to-cart-invoker" {
  project        = google_cloudfunctions_function.add-to-cart.project
  region         = google_cloudfunctions_function.add-to-cart.region
  cloud_function = google_cloudfunctions_function.add-to-cart.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}


#
# CheckoutCart Function
#

resource "google_cloudfunctions_function" "checkout-cart" {
  name = "checkout-cart-function"
  runtime = "python310"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.source-code.name
  source_archive_object = google_storage_bucket_object.checkout-cart-source-code.name
  trigger_http          = true
  entry_point           = "checkout_cart"
  min_instances = 1
  max_instances = 1
}

# Source code is stored at:
resource "google_storage_bucket_object" "checkout-cart-source-code" {
  name   = filesha256("./checkout_cart.zip")
  bucket = google_storage_bucket.source-code.name
  source = "./checkout_cart.zip"
}

# IAM permission for invoking the function
resource "google_cloudfunctions_function_iam_member" "checkout-cart-invoker" {
  project        = google_cloudfunctions_function.checkout-cart.project
  region         = google_cloudfunctions_function.checkout-cart.region
  cloud_function = google_cloudfunctions_function.checkout-cart.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}


#
# Firestore Database
#

resource "google_firestore_database" "carts-db" {
  app_engine_integration_mode       = "DISABLED"
  concurrency_mode                  = "PESSIMISTIC"
  delete_protection_state           = "DELETE_PROTECTION_DISABLED"
  deletion_policy                   = "ABANDON"
  location_id                       = "nam5"
  name                              = "carts-db"
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_DISABLED"
  project                           = "data-terminus-393416"
  type                              = "FIRESTORE_NATIVE"
}