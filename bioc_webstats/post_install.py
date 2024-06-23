import shutil
import os
import sys

def post_install():
    # Define the source and destination paths
    
    def copy_file(source_module, destination_directory, filename, set_executible=False):
        """Copy file from soucre_directory to destination_diretory"""

        source_directory = os.path.join(packages_path, source_module)
        source_full_name = os.path.join(source_directory, filename)
        if not os.path.isfile(source_full_name):
            print(f"Fail. {source_full_name} not found")
            return

        # Ensure the destination directory exists
        if not os.path.isdir(destination_directory):
            os.makedirs(destination_directory)
        
        destination_full_name = os.path.join(destination_directory, filename)
        shutil.copy(source_full_name, destination_full_name)
        if set_executible:
            current_permissions = os.stat(destination_full_name).st_mode
            os.chmod(destination_full_name, current_permissions | 0o111)


        print(f"OK. {source_full_name} -> {destination_full_name}")

        return
    
    anchor_path = os.path.normpath(os.path.dirname(__file__))
    packages_path = os.path.normpath(anchor_path + '/../')
    target_path = os.getenv('FLASK_APPROOT', default=os.getenv('HOME'))
    superd_path = os.path.join(target_path, "supervisord_programs")

    copy_file("", "", "app.wsgi")
    copy_file("supervisord_programs", '/etc/systemd/system', "bioc-webstats.service", True)
    copy_file("supervisord_programs", superd_path, "gunicorn.conf")
    copy_file("supervisord_programs", superd_path, "start_gunicorn.sh", True)

if __name__ == "__main__":
    post_install()
    print("post_install completed")