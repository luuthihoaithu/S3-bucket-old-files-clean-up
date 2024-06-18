#!/bin/bash

# Function to list old files
list_old_files() {
    bucket_name=$1
    folder_name=$2
    day_input=$3

    # Get current date and time
    current_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Calculate threshold date
    threshold_date=$(date -u -d"$current_date -$day_input days" +"%Y-%m-%dT%H:%M:%SZ")

    # List objects in the specified bucket and folder
    aws s3api list-objects-v2 --bucket $bucket_name --prefix $folder_name --query "Contents[?LastModified<=\`$threshold_date\` && !contains(Key, 'temp/')].{Key: Key, LastModified: LastModified}" --output text
}

# Function to delete old files
delete_old_files() {
    bucket_name=$1
    files=$2

    for file in $files
    do
        echo "Deleting $file"
        aws s3api delete-object --bucket $bucket_name --key $file
    done

    echo "Deletion complete."
}

# Main function
main() {
    echo "Enter S3 bucket name: "
    read bucket_name
    echo "Enter folder name (without trailing slash): "
    read folder_name
    echo "Enter day to delete: "
    read day_input
    
    # Check if the folder exists and has files older than specified days
    if ! aws s3 ls "s3://$bucket_name/$folder_name" >/dev/null 2>&1; then
        echo "Folder '$folder_name' does not exist or you do not have permission to access it."
        exit 1
    fi
    
    echo "Files older than $day_input days in folder '$folder_name' will be deleted."
    files_to_delete=$(list_old_files $bucket_name $folder_name $day_input)

    if [ -n "$files_to_delete" ]; then
        echo -e "\nFiles to be deleted from $folder_name:"
        echo "$files_to_delete"

        echo -e "\nDo you want to proceed with deletion? (yes/no): "
        read confirmation
        if [ "$confirmation" = "yes" ]; then
            delete_old_files $bucket_name "$files_to_delete"
        else
            echo "Deletion aborted."
        fi
    else
        echo "No files older than $day_input days found in $folder_name."
    fi
}

# Call main function
main
