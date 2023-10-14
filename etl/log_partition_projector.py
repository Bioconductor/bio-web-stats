#! /bin/python
import boto3

"""log_partition_projector - Move or Rename weblogs in s3 buckets to faciitate partition projection on dates

WIP
FOR TESTING: python3 log_partion_projector -s dev-bioc-weblogs-small-test -d dev-bioc-weblogs-small-test --dry-run 

"""

def log_partition_projector(source_bucket: str,
                            destination_bucket: str,
                            old_prefix: str,
                            dry_run: bool) -> int:

    if dry_run:
        '--dry_run selected. No modifications will be made'
    s3 = boto3.client('s3')
    # List the objects in the bucket with the specified prefix
    response = s3.list_objects_v2(Bucket=source_bucket, Prefix=old_prefix)

    if 'Contents' not in response:
        print("No files to process.")
        exit()

    for item in response['Contents']:
        filename = item['Key']
        
        # Extract date information from the filename
        date_parts = filename.split('.')[1].split('-')
        
        # TODO hard coded new prefix and dupicate on the right.
        new_key = f"weblogs/{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{date_parts[3]}/{filename}"
        print(new_key)
        if not dry_run:
        # TODO Check result code result['ResponseMetadata']['HTTPStatusCode']
            result = s3.copy_object(Bucket=destination_bucket, CopySource={'Bucket': source_bucket, 'Key': filename}, Key=new_key)
        
    # TODO stats
    print("Files rearranged successfully.")
    return 0

if __name__ == "__main__":
    from os import environ
    from sys import exit
    import argparse

    parser = argparse.ArgumentParser(description="Transform weblog default weblog filename formats to partionable format")
    
    parser.add_argument("-s", "--source", help="Source bucket")
    parser.add_argument("-d", "--destination", help="Destination bucket")
    parser.add_argument("-p", "--prefix", help="Destination bucket", default='')
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")

    environ['AWS_PROFILE'] = 'default'
    args = parser.parse_args()
    
    result_code = log_partition_projector(args.source, args.destination, args.prefix, args.dry_run)
    exit(result_code)

