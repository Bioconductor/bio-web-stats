#!/bin/bash

# Specify the source S3 bucket and prefix
SOURCE_BUCKET="dev-bioc-weblogs-small-test"
SOURCE_PREFIX=""
# Specify the destination prefix
DEST_PREFIX="source"

# Set the page size for listing objects
PAGE_SIZE=1000

# Initialize a token variable for pagination
token=""

# Loop until there are no more objects to list
while true
do
  # List objects in the source bucket with a page size and token
  objects=$(aws s3api list-objects-v2 --bucket "$SOURCE_BUCKET" --prefix "$SOURCE_PREFIX" --page-size "$PAGE_SIZE" --query 'Contents[].Key' --starting-token "$token")

  # Loop through the object keys and move them to the destination prefix
  for key in $objects
  do
    # Construct the source and destination paths
    source_path="s3://${SOURCE_BUCKET}/${key}"
    dest_key="${DEST_PREFIX}/${key#*/}" # Remove the existing prefix
    dest_path="s3://${SOURCE_BUCKET}/${dest_key}"

    # Move the object to the destination path
    aws s3 mv "$source_path" "$dest_path"
  done

  # Check if there are more objects to list
  token=$(aws s3api list-objects-v2 --bucket "$SOURCE_BUCKET" --prefix "$SOURCE_PREFIX" --page-size "$PAGE_SIZE" --query 'NextToken' --output text)

  if [ -z "$token" ] || [ "$token" == "None" ]; then
    break  # No more objects to list, exit the loop
  fi
done

echo "Objects at the top level moved to the '$DEST_PREFIX' prefix."
