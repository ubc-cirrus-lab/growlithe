from google.cloud import firestore
from growlithe_utils_gcp import getResourceProp

# Assuming your project ID is "my-project-123" and you have a collection named "users"
project_id = "my-project-123"
collection_name = "carts-db"

# Set up the Firestore client with your project
firestore.Client(project=project_id)

# Now you can use the getResourceProp function
resource = getResourceProp("Resource", "FIRESTORE_COLLECTION", collection_name)
print(f"Resource: {resource}")  # Output: Resource: users

region = getResourceProp("ResourceRegion", "FIRESTORE_COLLECTION", collection_name)
print(
    f"Region: {region}"
)  # Output: Region: my (assuming project ID format is "region-project-number")
