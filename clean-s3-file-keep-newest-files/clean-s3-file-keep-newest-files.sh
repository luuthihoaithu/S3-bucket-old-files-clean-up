#!/bin/bash

# Hàm để xóa các tệp trong thư mục của S3 bucket
delete_files() {
  local bucket_name=$1
  local folder_name=$2
  local num_files_to_keep=$3

  # Đảm bảo tên thư mục kết thúc bằng dấu gạch chéo
  if [[ "${folder_name: -1}" != "/" ]]; then
    folder_name="$folder_name/"
  fi

  # Đếm số lượng dấu gạch chéo trong folder_name để xác định cấp thư mục
  local folder_slash_count=$(echo "$folder_name" | grep -o "/" | wc -l)

  # Lấy danh sách các tệp trong thư mục được chỉ định và sắp xếp theo thời gian sửa đổi
  files_to_delete=$(aws s3api list-objects-v2 --bucket "$bucket_name" --prefix "$folder_name" \
    --query 'Contents[?ends_with(Key, `/`)==`false`].[Key, LastModified]' --output text | \
    awk -v fs_count=$folder_slash_count -v prefix=$folder_name '{
      # Lọc các tệp trong cùng một cấp thư mục
      if (gsub("/", "/", $1) == fs_count && index($1, prefix) == 1) {
        print $0
      }
    }' | sort -k2 -r | tail -n +$((num_files_to_keep + 1)))

  if [ -z "$files_to_delete" ]; then
    echo "No files found in the specified folder."
    return
  fi

  echo "The following files will be deleted:"
  echo "$files_to_delete"

  read -p "Do you want to continue? (yes/no): " confirm
  if [[ "$confirm" == "yes" ]]; then
    # Xóa các tệp đã xác nhận
    while read -r file; do
      key=$(echo $file | awk '{print $1}')
      aws s3api delete-object --bucket "$bucket_name" --key "$key"
    done <<< "$files_to_delete"
    echo "Files deleted successfully."
  else
    echo "Deletion cancelled."
  fi
}

# Nhập tên bucket, thư mục và số lượng tệp mới nhất cần giữ lại
read -p "Enter the name of the S3 bucket: " bucket_name
read -p "Enter the name of the folder: " folder_name
read -p "Enter the number of newest files to keep: " num_files_to_keep

delete_files "$bucket_name" "$folder_name" "$num_files_to_keep"
