"""get_bioc_package_history - Extract Bioconductor package history from source repo"""
import logging
import yaml
import requests
import bioc_webstats.models as db


from flask import current_app

# Local manifest constants
BIOCONDUCTOR_HOME_URI = "https://www.bioconductor.org/"
PACKAGE_CATEGORIES = ["bioc", "data-annotation", "data-experiment", "workflows"]
PACKAGE_UPDATE_MAXIMUM_ALLOWED = 50

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


def packages_table_update(dry_run:bool, verbose:bool, force:bool):
    """Update database table packages from manifests on www.bioconductor.org

    Keyword Arguments:
        dry_run -- Calcluate changes to packges but do not update the database (default: {False})
        verbose -- Additional information to log file (default: {True})
        force -- Proceed with update even if the number of changes exceeds PACKAGE_UPDATE_MAXIMUM_ALLOWED. (default: {False})

    Returns:
        _description_
    """
    
    log = current_app.logger
    log.log(logging.INFO, f'starting pacakges update')

    bioconductor_config = yaml.safe_load(web_download("config.yaml"))
    
    release_version = bioconductor_config["release_version"]
    devel_version = bioconductor_config["devel_version"]
    
    manifest_packages = {}
    for category in PACKAGE_CATEGORIES:
        package_text = web_download(f"packages/devel/{category.replace("-", "/")}/src/contrib/PACKAGES")
        package_list = package_text.splitlines()
        p = {line.split(": ")[1]: db.PackageType[category.removeprefix("data-").upper()] for line in package_list if line.startswith("Package:")}
        manifest_packages.update(p)
        
    # dev_pcakages represents the currently active packages in the "devel" version.
    # all_packages is the complete package history
    # A package that is in dev but not all is new in the devel version
    #   and so will be added with first_version set to the devel version and last_version set to NULL
    # A package that is in all but not dev has been removed from the last version
    #   and so will have its last_version value set to the release_version
    # If it is in both dev and all, the last_version should be null. If it is not, then
    #   the package was reinstated in the devel release and the last_version will be reset to NULL
    
    dev_packages = set(manifest_packages.keys())
    # the Packages model will return 4-tuples. Turn this into a dictionary, indexted by package name
    all_package_details = db.Packages.all_package_details()
    all_active_packages = {t[0] for t in all_package_details if t[3] is None}
    all_inactive_packages = {t[0] for t in all_package_details} - all_active_packages
    
    new_package_names = dev_packages - all_active_packages
    removed_package_names = all_active_packages - dev_packages
    reinstated_package_names = all_inactive_packages & dev_packages
    if (verbose):
        log.log(logging.INFO, f"Total packages before update: {len(all_package_details)}")
        log.log(logging.INFO, f"Packages removed: {len(removed_package_names)}")
        log.log(logging.INFO, f"Packages added: {len(new_package_names)}")
        log.log(logging.INFO, f"Packages reinstated: {len(reinstated_package_names)}")
    
    total_changes = len(removed_package_names) + len(reinstated_package_names) + len(new_package_names)
    if total_changes > PACKAGE_UPDATE_MAXIMUM_ALLOWED:
        log.log(logging.WARN, f"total number of changes ({total_changes}) excceds maximum allowed ({PACKAGE_UPDATE_MAXIMUM_ALLOWED})")
        if not force:
            log.log(logging.ERROR, "No update made")
            return
        log.log(logging.WARN, "Force parameter is TRUE. Update will proceed")
    
    # mark the inactive packages with the value of the last release
    db.Packages.update_package_last_version(removed_package_names, release_version)
    # mark any reinstated packages by setting the last_vesion to NLL
    db.Packages.update_package_last_version(reinstated_package_names, None)
    # insert any new packages
    records = [{"package": package, "category": manifest_packages[package], "first_version": devel_version, "last_version": None} for package in new_package_names]
    if (len(records) > 0):
        db.Packages.insert_records(records)
    log.log(logging.INFO, "Update complete.")
    return

