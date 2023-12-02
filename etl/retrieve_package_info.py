"""Standalone program to fetch all known package names and store them in S3."""
import re

import boto3
import requests

source_url = 'https://git.bioconductor.org'
bucket_name = "web-stats-dev"
key = "gitdata/packagenames"


def fetch_packagenames(url):
    """Read the package names from the root of git.bioconductor.org."""
    response = requests.get(url)
    response.raise_for_status()
    result = re.findall(r"^\ R\s+packages/([A-Za-z0-9\.\_]+)$", response.text, re.MULTILINE)
    return result


def store_data_s3(bucket_name, key, data):
    """Stoe the data in S3."""
    s3 = boto3.client('s3')
    result = s3.put_object(Bucket=bucket_name, Key=key, Body=data)
    return result
    # TODO Test for errors


data = fetch_packagenames(source_url)
result = store_data_s3(bucket_name=bucket_name, key=key, data='\n'.join(data))
pass
# TODO check for success
