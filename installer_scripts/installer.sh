#!/bin/bash
# usage script installer.sh TARGET_PLATFORM
#  TARGET_PLATFORM = EC2 | docker (default is EC2)

TARGET_PLATFORM="${1:-EC2}"
echo "Starting installation of bioc-webstats"
echo $(date -R)
if [ "$TARGET_PLATFORM" != "EC2" ] && [ "$TARGET_PLATFORM" != "docker" ]; then
    echo "Error: Platform must be either 'EC2' or 'docker'."
    exit 1
else
    echo "TARGET_PLATFORM=$TARGET_PLATFORM"
fi


sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3.12-venv curl unzip nano vim tree -y

python3 -m venv .venv
. .venv/bin/activate

wheel_file="$(ls -1t bioc_webstats*.whl| sort | head -1)"
# install the newest wheel file in sort order
cd ~
pip install $wheel_file

aws_location=$(which aws)

if [ -z "$aws_location" ]; then
    if [ "$TARGET_PLATFORM" = "EC2" ]; then
        sudo snap install aws-cli --classic
    else
    . $(find .venv/lib/ -name aws_installer.sh)
    fi
fi

if [ ! -e ~/.aws/config ]; then
    mkdir -p ~/.aws
    cat > .aws/config <<eof
[profile default]
sso_session = webstats
sso_account_id = 931729544676
sso_role_name = AdministratorAccess
region = us-east-1
output = json
[sso-session webstats]
sso_start_url = https://bioconductor.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
eof

fi

. $(find .venv/lib/ -name flask_environment)


sudo mkdir -p $FLASK_APPROOT
sudo chown -R $FLASK_OSUSER:$FLASK_OSGROUP $FLASK_APPROOT

sudo mkdir -p $FLASK_LOGROOT
sudo chown -R $FLASK_OSUSER:$FLASK_OSGROUP $FLASK_LOGROOT

# create bioc-webstats.service part 1
cat > bioc-webstats.service <<eof
[Unit]
Description=Waitress service for www-webstats
After=network.target

[Service]
eof

# create bioc-webstats.service part 2, then environment variables

# Initialize an empty string to hold the environment variables
env_string="Environment="

# Loop through all environment variables
while IFS='=' read -r name value ; do
  # Check if the variable name starts with "FLASK_"
  if [[ $name == FLASK_* ]]; then
    # Remove the "FLASK_" prefix from the variable name
    env_string+="\"${name}=${value}\" "
  fi
done < <(env)

# Trim the trailing space and print the result
env_string=$(echo "$env_string" | sed 's/ $//')

echo "$env_string" >> bioc-webstats.service 

# part 3, the rest of the file.
cat >> bioc-webstats.service <<eof
WorkingDirectory=/home/ubuntu
ExecStart=/home/ubuntu/.venv/bin/python3 -m bioc_webstats.app_waitress

[Install]
WantedBy=multi-user.target
eof

sudo cp bioc-webstats.service /etc/systemd/system/
# TODO clean up local copy of bioc-webstats.service
sudo chown root:root /etc/systemd/system/bioc-webstats.service
sudo chmod 644 /etc/systemd/system/bioc-webstats.service
sudo cp "$(find .venv/lib/ -name flask_environment)" $FLASK_APPROOT/
sudo chown root:root /etc/systemd/system/bioc-webstats.service
sudo chmod 644 $FLASK_APPROOT/flask_environment


sudo systemctl enable bioc-webstats.service
sudo systemctl start bioc-webstats.service
sudo systemctl status bioc-webstats.service
# TODO move flask_ingest.sh and flask_ingest_crontabs_setup.sh to target machiine