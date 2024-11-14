Specimen log rotation configuration for the web app.

Place the file installer_scripts/logrotate.d/bioc-webstats
on the target system under /etc/logrotate.d/

Then set owner to root
sudo chown root:root bioc-webstats 

Test by running:
sudo logrotate -d /etc/logrotate.d/bioc-webstats