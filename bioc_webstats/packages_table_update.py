"""get_bioc_package_history - Extract Bioconductor package history from source repo"""
import logging
import yaml
import requests
import bioc_webstats.models as db


from flask import current_app

# Local manifest constants
BIOCONDUCTOR_HOME_URI = "https://www.bioconductor.org/"
PACKAGE_CATEGORIES = ["bioc", "data-annotation", "data-experiment", "workflows"]
    
def version_str_to_int(version_number:chr):
    parts = version_number.split('.')
    if len(parts) == 2:
        return int(parts[0]) * 100 + int(parts[1])
    else:
        raise ValueError(f"Invalid version number: {version_number}")

def version_int_to_str(version_int: int):
    return f"{version_int // 100}.{version_int % 100}"
    
def web_download( stem:str, fqdn: str = BIOCONDUCTOR_HOME_URI):
    uri = f"{fqdn}{stem}"
    response = requests.get(uri)
    if response.status_code != 200:
        raise ValueError(f"Failed to download file from {uri}")
    return response.text


def packages_table_update(dry_run:bool = False, verbose: bool = True, force: bool = False):
    """Update packages table from web    
    Args:
        TODO

    Returns:
        TODO
    """

    bioconductor_config = yaml.safe_load(web_download("config.yaml"))
    
    release_version = bioconductor_config["release_version"]
    devel_version = bioconductor_config["devel_version"]
    
    # TODO manage any possible changes in category. (rare but should be taken into account)
    dev_packages = []
    for category in PACKAGE_CATEGORIES:
        package_text = web_download(f"packages/devel/{category.replace("-", "/")}/src/contrib/PACKAGES")
        package_list = package_text.splitlines()
        package_names = [line.split(": ")[1] for line in package_list if line.startswith("Package:")]
        dev_packages.extend(package_names)

    # dev_pcakages represents the currently active packages in the "devel" version.
    # all_packages is the complete package history
    # A package that is in dev but not all is new in the devel version
    #   and so will be added with first_version set to the devel version and last_version set to NULL
    # A package that is in all but not dev has been removed from the last version
    #   and so will have its last_version value set to the release_version
    # If it is in both dev and all, the last_version should be null. If it is not, then
    #   the package was reinstated in the devel release and the last_version will be reset to NULL
    
    
    dev_packages = set(dev_packages)
    # the Packages model will return 4-tuples. Turn this into a dictionary, indexted by package name
    all_package_details = db.Packages.all_package_details()
    all_active_packages = {t[0] for t in all_package_details if t[3] is None}
    all_inactive_packages = {t[0] for t in all_package_details} - all_active_packages
    
    new_package_names = dev_packages - all_active_packages
    removed_package_names = all_active_packages - dev_packages
    reinstated_package_names = all_inactive_packages & dev_packages
    # TODO add new_package_names
    # TODO mark removed_package_names last_verion <- release_version
    # TODO mark reinstated_package_names last_Version <- NULL
    # TODO report numbers for each of the above
    return dev_packages


def update_packages():
    history = packages_table_update()
    # TODO transform and save
    pass