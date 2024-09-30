# Start the server
docker run --privileged --name=webstats1 -d webstats-server
# Retrieve the local ip address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' webstats1
# Move the most recent whl file to the docker container
docker cp  "$(ls -1ar ../dist/bioc_webstats-*.whl|head -1)" webstats1:/home/ubuntu
# login
docker exec -it --user ubuntu webstats1 /bin/bash
