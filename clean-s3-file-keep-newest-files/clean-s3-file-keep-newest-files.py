import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from operator import itemgetter

# Create a session using your AWS credentials
s3 = boto3.resource('s3')

def delete_files(bucket_name, folder_name, num_files_to_keep):
    try:
        bucket = s3.Bucket(bucket_name)
        
        # Check if the bucket exists by attempting to access it
        s3.meta.client.head_bucket(Bucket=bucket_name)
        
        files_to_delete = []

        # Ensure the folder name ends with a slash to properly filter objects
        if not folder_name.endswith('/'):
            folder_name += '/'

        # List all file objects within the specified folder
        for obj in bucket.objects.filter(Prefix=folder_name):
            # Only consider files directly in the specified folder, not in subfolders
            if obj.key.endswith('/') or obj.key.count('/') > folder_name.count('/'):
                continue
            files_to_delete.append({'Key': obj.key, 'LastModified': obj.last_modified})

        if not files_to_delete:
            print("No files found in the specified folder.")
            return

        # Sort files by last modified timestamp
        files_to_delete.sort(key=itemgetter('LastModified'), reverse=True)

        # Identify the files to be deleted
        files_to_delete = files_to_delete[num_files_to_keep:]

        # Display the list of files to be deleted and ask the user to confirm the deletion
        if files_to_delete:
            print("The following files will be deleted:")
            for file in files_to_delete:
                print(f"File: {file['Key']}, Last Modified: {file['LastModified']}")


            confirm = input("Do you want to continue? (yes/no): ")
            if confirm.lower() == 'yes':
                # Delete the confirmed files
                bucket.delete_objects(Delete={'Objects': files_to_delete})
            else:
                print("Deletion cancelled.")
        else:
            print(f"There are no files older than the {num_files_to_keep} newest files.")
    
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Error: The bucket '{bucket_name}' does not exist.")
        else:
            print(f"Error: {e.response['Error']['Message']}")

bucket_name = input("Enter the name of the S3 bucket: ")
folder_name = input("Enter the name of the folder: ")
num_files_to_keep = int(input("Enter the number of newest files to keep: "))

delete_files(bucket_name, folder_name, num_files_to_keep)
