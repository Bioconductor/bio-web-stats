#!/bin/bash

sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3.12-venv curl unzip nano vim tree -y

# from host scp -P 2222 dist/bioc_webstats-0.1.6-py3-none-any.whl ubuntu@localhost:.
python3 -m venv .venv
. .venv/bin/activate

pip install bioc_webstats-0.1.6-py3-none-any.whl

# TODO only run this if aws is not installed
# TODO on EC2 - sudo apt  install awscli
# . aws_installer.sh
# curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# unzip awscliv2.zip
# sudo ./aws/install
# aws --version


# # TODO aws config info -- condition on availabiity of role
# cat > .aws/config <<eof
# [profile default]
# sso_session = webstats
# sso_account_id = 931729544676
# sso_role_name = AdministratorAccess
# region = us-east-1
# output = json
# [sso-session webstats]
# sso_start_url = https://bioconductor.awsapps.com/start
# sso_region = us-east-1
# sso_registration_scopes = sso:account:access
# eof

### End of awscli install

# TODO Create/verify aws role. default: bioc-webstats-webrunner
# TODO Need to make log directory available for update

sudo mkdir -p /var/log/bioc-webstats
sudo chown -R ubuntu /var/log/bioc-webstats

sudo mkdir -p /var/www/bioc-webstats
sudo chown -R ubuntu /var/www/bioc-webstats

# TODO parameterize
export FLASK_APP="bioc_webstats.app:create_app('Production')"
export FLASK_AWS_PATH_PARAMETER=/bioc/webstats/prod
export FLASK_APPROOT=/var/www/bioc-webstats/

python -m bioc_webstats.post_install

cd /var/www/bioc-webstats/supervisord_programs/
sudo systemctl enable bioc-webstats.service
sudo systemctl start bioc-webstats.service
sudo systemctl status bioc-webstats.service
