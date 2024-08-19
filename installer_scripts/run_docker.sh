docker run -p 2222:22 -p 5555:5000 --privileged --name=webstats1 -d webstats-server

docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' webstats1


docker cp  "$(ls -1ar ../dist/bioc_webstats-*.whl|head -1)" webstats1:/home/ubuntu
docker exec -it --user ubuntu webstats1 /bin/bash
