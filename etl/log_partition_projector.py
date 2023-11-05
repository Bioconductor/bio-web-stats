#! /bin/python
import argparse
from os import environ

import boto3

"""log_partition_projector - Move or Rename weblogs in s3 buckets to faciitate partition projection on dates

WIP
FOR TESTING:
python3 log_partion_projector -s bioc-cloudfront-logs -d web-stats-dev --dryrun

"""


def log_partition_projector(
    source_bucket: str,
    destination_bucket: str,
    old_prefix: str,
    new_prefix: str,
    dryrun: bool,
    first: str
) -> int:

    s3 = boto3.client('s3')

    def fetch_objects(bucket_name, prefix):
        continuation_token = None

        while True:
            list_kwargs = {
                'Bucket': bucket_name,
                'Prefix': prefix,
                'StartAfter': first
            }
            if continuation_token:
                list_kwargs['ContinuationToken'] = continuation_token

            response = s3.list_objects_v2(**list_kwargs)
            yield from response.get('Contents', [])

            if not response.get('IsTruncated'):  # Stop iteration if no more files
                break

            continuation_token = response.get('NextContinuationToken')

    if dryrun:
        "--dryrun selected. No modifications will be made"
    object_count = 0

    for item in fetch_objects(source_bucket, old_prefix):
        filename = item["Key"]
        # Extract date information from the filename
        date_parts = filename.split(".")[1].split("-")

        # TODO parameterie hard coded new prefix
        new_key = (
            f"{new_prefix}/{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{filename}"
        )
        print(new_key)
        object_count += 1
        if not dryrun:
            s3.copy_object(
                Bucket=destination_bucket,
                CopySource={"Bucket": source_bucket, "Key": filename},
                Key=new_key,
            )
        pass

    print(f"{object_count} objects rearranged.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform weblog default weblog filename formats to partionable format"
    )

    parser.add_argument("-s", "--source", required=True, help="Source bucket")
    parser.add_argument("-d", "--destination", required=True, help="Destination bucket")
    parser.add_argument("-p", "--prefix", help="Old (Source) prefix", default="")
    parser.add_argument(
        "-n", "--newprefix", help="New (Destination) prefix", default="weblogs"
    )
    parser.add_argument("-f", "--first", help="Start after this string")
    parser.add_argument(
        "-m", "--move", action="store_true", help="If move then source will be deleted"
    )
    parser.add_argument("--dryrun", action="store_true", help="Run in dry-run mode")

    # HACK cli: aws --profile prod sso login
    environ["AWS_PROFILE"] = "prod"

    test_args = "-s bioc-cloudfront-logs -d web-stats-dev -n weblogs -f E1TVLJONPTUXV3.2023-05".split(" ")
    # TODO DEBUG ONLY
    args = parser.parse_args(test_args)

    result_code = log_partition_projector(
        args.source, args.destination, args.prefix, args.newprefix, args.dryrun, args.first
    )
    exit(result_code)
