# Setting up a ubuntu/dev environment
This is an example that shows the basic steps in assembling a webstats environmewnt for an ubuntubased developer.
It does not include the installtion of an IDE.
## Creating the container
Start in the home directory of a current clone of the bioconductor/bio-web-stats repo
```bash
cd ~/Projects/bio-web-stats/installer_scripts/
source ./build_docker.sh
```
We now have a docker image named  `webstats-server` We will create a container and clone the source repo.
```bash
docker run --privileged  -p 5000:5000 -p 22:22 -p 80:80 --name=webstats-dev -d webstats-server
# Here is the local IP address for ther server
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' webstats-dev
```
Note the IP address reported (ysually, `172.17.0.2`). Connect to the server.

```bash
docker exec -it --user ubuntu webstats-dev /bin/bash
```

If you want to run postgres, install it.
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib 
```

Now clone the repo and install poetry.
```bash
cd $HOME
# verify that the working directory is now /home/ubuntu/
pwd
git clone https://github.com/bioconductor/bio-web-stats.git
cd bio-web-stats
pipx install poetry
pipx ensurepath
. ~/.bashrc
# Build the app and see if it is working.
poetry install
```

The application is now installed. Accessing the applicaiton and any of its utilities can be accomplished with this command

```bash
export FLASK_APP=autoapp.py
poetry run flask --help
```

If everything worked correctly you should see output that looks like this.
```
Usage: flask [OPTIONS] COMMAND [ARGS]...

  A general utility script for Flask applications.
  ... more ...
  
Commands:
  configp  Initialize AWS parameter set
  db       Perform database migrations.
  digest   md5 tag and compress static files.
  gendb    Generate small test database.
  ingest   Read raw weblogs, select valid package downlads, update...
  lint     Lint and check code style with black, flake8 and isort.
  routes   Show the routes for the app.
  run      Run a development server.
  shell    Run a shell in the app context.
  test     Run the tests.
  ```
  If you have the "ingest" and "gendb" commands, flask is attacched to the webtats application.
  To start a development server, 

  In addition to poetry run command, you can also open a new shell which will have the
  poetry environment available.
  ```shell
poetry shell
```
Now, you are within the shell but in the poetry environment.
The prompt should looks something like this: `(bioc-webstats-py3.12) ubuntu@88dc3287cc84:~/bio-web-stats$ `

Run these commands:
```bash
flask test
flask gendb
# the --host parameter directs the development web server to bind to all IP addresses
flask run --host="0.0.0.0"
```
You should now see this:
```
 * Serving Flask app 'autoapp.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
Press CTRL+C to quit
```
and be able to access the site locally via `http://127.0.0.1:5000/packages/stats/`.

If you also want to run it on the host machine, you should `flask run --host=0.0.0.0`. Then
(assuming that the local IP address of the server is `172.17.0.2`) you can access the site at 
`http://172.17.0.2:5000/packages/stats/`.
