#!/bin/bash
export TARGET_PLATFORM=EC2


sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3.12-venv curl unzip nano vim tree -y

# from host scp -P 2222 dist/bioc_webstats-0.1.6-py3-none-any.whl ubuntu@localhost:.
python3 -m venv .venv
. .venv/bin/activate


pip install bioc_webstats-0.1.7-py3-none-any.whl

# TODO only run this if aws is not installed
# TODO on EC2 - sudo apt install awscli
# on docker:
# . aws_installer.sh


# # # TODO aws config info -- condition on availabiity of role
# mkdir .aws
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

export FLASK_APP="bioc_webstats.app:create_app('production', '/bioc/webstats/prod')"
export FLASK_AWS_PATH_PARAMETER=/bioc/webstats/prod
export FLASK_OSUSER="webstats"
export FLASK_OSGROUP="webstats"
export FLASK_APPROOT="/var/www/bioc-webstats"
# TODO need configmodule entry for FLASK_LOGROOT
export FLASK_LOGROOT="/var/log/bioc-webstats"
export AWS_PARAMETER_PATH='/bioc/webstats/prod'

sudo mkdir -p $FLASK_APPROOT
sudo chown -R $FLASK_OSUSER $FLASK_APPROOT

sudo mkdir -p $FLASK_LOGROOT
sudo chown -R $FLASK_OSUSER $FLASK_LOGROOT


# TODO put this in python -m bioc_webstats.post_install with generation of flask_environment and bioc-webstats.service
sudo cp ~/.venv/lib/python3.12/site-packages/supervisord_programs/bioc-webstats.service /etc/systemd/system/
sudo cp ~/.venv/lib/python3.12/site-packages/supervisord_programs/flask_environment $FLASK_APPROOT
sudo chown $FLASK_OSUSER:$FLASK_OSGROUP $FLASK_APPROOT
sudo chmod +x $FLASK_APPROOT
sudo systemctl enable bioc-webstats.service
sudo systemctl start bioc-webstats.service
sudo systemctl status bioc-webstats.service
# TODO move flask_ingest.sh and flask_ingest_crontabs_setup.sh to target machiine