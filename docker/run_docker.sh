docker run -p 2222:22 -p 5555:5000 --privileged --name=webstats1 -d webstats-server

docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' webstats1
