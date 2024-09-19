"""get_bioc_package_history - Extract Bioconductor package history from source repo"""
import logging
import os
import git
import tempfile
import shutil
import yaml
import requests
import pandas as pd

from flask import current_app

# Local manifest constants
BIOCONDUCTOR_MANIFEST_URL = "https://git.bioconductor.org/admin/manifest"
BIOCONDUCTOR_PINNACLE_CONFIGURATION = "https://bioconductor.org/config.yaml"
PACKAGE_CATEGORIES = ["data-annotation", "data-experiment", "software", "workflows"]


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
    
def version_number_integer(number):
    parts = number.split('.')
    if len(parts) == 2:
        return int(parts[0]) * 100 + int(parts[1])
    else:
        raise ValueError(f"Invalid version number: {number}")
    

def packages_table_update(first_version=None, last_version=None):
    """
    Retrieve the Bioconductor package history from the source repository.
    
    Args:
        first_version (str): The first version to include in the update. Default: start at the first version
        last_version (str): The last version to include in the update. Default: through the last version

    Returns:
        DataFrame: With columns (version, cateogry, package_names)
    """

    if first_version is None:
        lower_limit = 0
    else:
        lower_limit = version_number_integer(first_version)
    
    if last_version is None:
        upper_limit = 99999
    else:
        upper_limit = version_number_integer(last_version)
    
    
    package_history = pd.DataFrame(columns=["version", "category", "package_name"])

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

    try:
        # Clone the Bioconductor manifest repository
        repo = git.Repo.clone_from(BIOCONDUCTOR_MANIFEST_URL, cloned_repo_dir)
        
        # Iterate over each branch in the repository
        for branch in repo.remote().refs:
            if branch.name.startswith('origin/RELEASE_'):
                version_number = version_number_integer(version_label_to_number(branch.name))
                # Note: can't use islice because the branch names are not termporally ordered
                if version_number >= lower_limit and version_number <= upper_limit:

                    # Checkout the branch
                    repo.git.checkout(branch.name)
                    
                    # Read the manifest file
                    for category in PACKAGE_CATEGORIES:
                        category_file_path = f"{cloned_repo_dir}/{category}.txt"
                        if os.path.exists(category_file_path):
                            with open(category_file_path, 'r') as category_file:
                                for line in category_file:
                                    if line.startswith("Package: "):
                                        new_row = pd.DataFrame([{
                                            "version": version_number,
                                            "category": category,
                                            "package_name": line.strip().replace("Package: ", "")
                                        }])
                                        package_history = pd.concat([package_history, new_row], ignore_index=True)
        
    finally:
        # Clean up the temporary directory
        shutil.rmtree(cloned_repo_dir)

    summary = package_history.groupby(['category', 'package_name']).agg(
        first_version=('version', 'min'),
        last_version=('version', 'max')
    ).reset_index()
    pass
    return summary



def update_packages():
    history = packages_table_update("3.17")
    # TODO transform and save
    pass