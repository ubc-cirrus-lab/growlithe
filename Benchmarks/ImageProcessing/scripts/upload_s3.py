import boto3
import os

# Initialize S3 client
s3_client = boto3.client("s3")

# Configuration
USER_BUCKET_NAME = "sam-user-images"
ADVERT_BUCKET_NAME = "sam-advert-images"


def upload_image_to_s3(file_path, bucket_name):
    """Upload an image to the specified S3 bucket in the 'raw/' prefix"""
    file_name = os.path.basename(file_path)
    object_key = f"raw/{file_name}"

    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        print(f"Successfully uploaded {file_name} to {bucket_name}/{object_key}")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {str(e)}")
        return False


def main():
    # Path to the image file you want to upload
    image_path = "path/to/your/image.jpg"  # Replace with the path to your image

    # Choose which bucket to upload to
    bucket_choice = input(
        "Enter 'user' to upload to User bucket or 'advert' to upload to Advert bucket: "
    ).lower()

    if bucket_choice == "user":
        bucket_name = USER_BUCKET_NAME
    elif bucket_choice == "advert":
        bucket_name = ADVERT_BUCKET_NAME
    else:
        print("Invalid choice. Please enter 'user' or 'advert'.")
        return

    # Upload the image to S3
    success = upload_image_to_s3(image_path, bucket_name)

    if success:
        print(
            "Image uploaded successfully. The Step Function will be triggered automatically."
        )
    else:
        print("Failed to upload the image. The Step Function will not be triggered.")


if __name__ == "__main__":
    main()
