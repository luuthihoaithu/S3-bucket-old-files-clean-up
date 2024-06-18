import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone

def list_old_files(bucket_name, folder_name, day_input):
    s3 = boto3.client('s3')
    
    files_to_delete = []
    today = datetime.now(timezone.utc)  # Chuyển đổi ngày giờ hiện tại sang UTC
    threshold = today - timedelta(days=int(day_input))

    try:
        # List objects in the specified bucket and folder
        paginator = s3.get_paginator('list_objects_v2')
        operation_parameters = {'Bucket': bucket_name, 'Prefix': folder_name}

        # Check if the folder exists by attempting to list objects
        folder_exists = False
        for result in paginator.paginate(**operation_parameters):
            for obj in result.get('Contents', []):
                folder_exists = True
                # Extract file creation date (as UTC)
                file_last_modified = obj['LastModified'].replace(tzinfo=timezone.utc)
                # Check if the object is a file and older than threshold
                # Ensure it's not the folder or subfolders
                if obj['Key'] != folder_name + '/' and not obj['Key'].endswith('/') and '/' not in obj['Key'][len(folder_name) + 1:]:
                    if file_last_modified < threshold:
                        files_to_delete.append({
                            'Key': obj['Key'],
                            'LastModified': obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                        })

        if not folder_exists:
            print(f"Error: The folder '{folder_name}' does not exist in the bucket '{bucket_name}'.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"Error: The bucket '{bucket_name}' does not exist.")
        else:
            print(f"Error: {e.response['Error']['Message']}")
        return None

    return files_to_delete

def delete_old_files(bucket_name, files):
    s3 = boto3.client('s3')
    
    for file in files:
        print(f"Deleting {file['Key']} (Last modified: {file['LastModified']})")
        s3.delete_object(Bucket=bucket_name, Key=file['Key'])

    print("Deletion complete.")

def main():
    bucket_name = input("Enter S3 bucket name: ")
    folder_name = input("Enter folder name (without trailing slash): ")
    day_input = input("Enter day to delete: ")

    files_to_delete = list_old_files(bucket_name, folder_name, day_input)

    if files_to_delete is not None and files_to_delete:
        print(f"\nFiles to be deleted from {folder_name}:")
        for file in files_to_delete:
            print(f"- {file['Key']} (Last modified: {file['LastModified']})")
        
        confirmation = input("\nDo you want to proceed with deletion? (yes/no): ").lower().strip()
        if confirmation == 'yes':
            delete_old_files(bucket_name, files_to_delete)
        else:   
            print("Deletion aborted.")
    elif files_to_delete == []:
        print(f"No files older than {day_input} days found in {folder_name}.")

if __name__ == "__main__":
    main()
