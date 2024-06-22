sudo apt update
sudo apt upgrade
sudo apt install python3 python3-venv curl unzip nano vim -y
# from host scp -P 2222 dist/bioc_webstats-0.1.5-py3-none-any.whl ubuntu@localhost:.
python3 -m venv .venv
. .venv/bin/activate

pip install bioc_webstats-0.1.5-py3-none-any.whl

. aws_installer.sh
# curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# unzip awscliv2.zip
# sudo ./aws/install
aws --version


# TODO aws config info -- condition on availabiity of role
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
