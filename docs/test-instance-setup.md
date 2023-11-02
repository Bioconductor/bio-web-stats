# Stats Test Instance Setup

## Deploy EC2 Instance
- Deploy an EC2 Instance with Ubuntu 22.04, Instance type: t2.micro.

## 1. Prepare Ubuntu Server
- Update the system and install Apache and mod_wsgi:
  - `sudo apt update`
  - `sudo apt upgrade`
  - `sudo apt install apache2 libapache2-mod-wsgi-py3`

## 2. Install Required Software
- Install Python 3 and pip:
  - `sudo apt install python3-pip`

## 3. Configure Apache
- Enable the mod_wsgi module for Apache:
  - `sudo a2enmod wsgi`

## 4. Create Flask Application
- Place the Flask application code on the server.
- Create a directory for your Flask app and clone your code into it.
- Create a Python virtual environment to manage your dependencies:
  - `cd /var/www/`
  - `git clone https://github.com/Bioconductor/bio-web-stats.git`
  - `cd /var/www/bio-web-stats`
  - `python3 -m venv venv`
  - `source venv/bin/activate`
  - `pip install -r /requirements/dev.txt`

## 5. Configure Apache Virtual Host
- Create an Apache Virtual Host configuration file for the Flask app.
- Modify the configuration to suit your specific paths:
  - `sudo nano /etc/apache2/sites-available/000-default.conf`

  ```apache
  <VirtualHost *:80>
      ServerName 18.117.254.107
      WSGIDaemonProcess app user=www-data group=www-data threads=5
      WSGIScriptAlias / /var/www/test4/bio-web-stats/app.wsgi
      <Directory /var/www/test4/bio-web-stats/bioc_webstats>
          WSGIProcessGroup app
          WSGIApplicationGroup %{GLOBAL}
          Require all granted
      </Directory>
      ErrorLog ${APACHE_LOG_DIR}/error.log
      CustomLog ${APACHE_LOG_DIR}/access.log combined
  </VirtualHost>
