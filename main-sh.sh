#!/bin/bash

# Hiển thị menu
echo "AWS-Toolkit:"
echo "1. clean-s3-file-keep-newest-files"
echo "2. clean-s3-file-with-day"
echo "3. exit"

# Đọc lựa chọn của người dùng
read -p "function: " choice

# Xử lý lựa chọn của người dùng
case $choice in
    1)
        echo "---clean-s3-file-keep-newest-files---"
        ./clean-s3-file-keep-newest-files/clean-s3-file-keep-newest-files.sh
        ;;
    2)
        echo "---clean-s3-file-with-day---"
        ./clean-s3-file-after-day/clean-s3-file-after-day.sh
        ;;
    3)
        echo "Exit."
        exit 0
        ;;
    *)
        echo "Invalid selection!"
        ;;
esac
