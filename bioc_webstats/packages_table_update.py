"""get_bioc_package_history - Extract Bioconductor package history from source repo"""
import logging
import git
import tempfile
import shutil
import yaml
import requests

from flask import current_app

# Local manifest constants
BIOCONDUCTOR_MANIFEST_URL = "https://git.bioconductor.org/admin/manifest"
BIOCONDUCTOR_PINNACLE_CONFIGURATION = "https://bioconductor.org/config.yaml"


def version_label_to_number(label):
    """
    Convert a version label to a version number.
    
    Args:
        label (str): The version label (e.g., 'origin/RELEASE_3_15').
        
    Returns:
        str: The version number (e.g., '3.15').
    """
    parts = label.split('_')
    if len(parts) >= 3:
        return f"{parts[-2]}.{parts[-1]}"
    else:
        raise ValueError(f"Invalid version label: {label}")

def version_number_to_label(number):
    """
    Convert a version number to a version label.
    
    Args:
        number (str): The version number (e.g., '3.15').
        
    Returns:
        str: The version label (e.g., 'origin/RELEASE_3_15').
    """
    parts = number.split('.')
    if len(parts) == 2:
        return f"origin/RELEASE_{parts[0]}_{parts[1]}"
    else:
        raise ValueError(f"Invalid version number: {number}")

def packages_table_update():

    # Create a temporary directory
    cloned_repo_dir = tempfile.mkdtemp()

    # get the bioconductor corpus configuration

    response = requests.get(BIOCONDUCTOR_PINNACLE_CONFIGURATION)
    if response.status_code == 200:
        bioconductor_config = yaml.safe_load(response.text)
    else:
        raise ValueError(f"Failed to fetch configuration from {BIOCONDUCTOR_PINNACLE_CONFIGURATION}")

    release_version = bioconductor_config["release_version"]
    devel_version = bioconductor_config["devel_version"]
    release_dates = bioconductor_config["release_dates"]

    repo = git.Repo.clone_from(BIOCONDUCTOR_MANIFEST_URL, cloned_repo_dir)
    remote_branches = [ref.name for ref in repo.remote().refs]

    pass


    shutil.rmtree(cloned_repo_dir)
