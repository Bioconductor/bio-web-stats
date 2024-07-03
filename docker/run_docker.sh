docker run -p 2222:22 -p 5555:5000 --privileged --name=webstats1 -d webstats-server

docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' webstats1

# docker exec -it --user root webstats1 /bin/bash
# docker exec -it --user ubuntu webstats1 /bin/bash
# docker exec -it --user webstats webstats1 /bin/bash
# docker cp dist/bioc_webstats-0.1.8-py3-none-any.whl webstats1:/home/ubuntu/
# docker cp  "$(ls -1a dist/bioc_webstats-*.whl|head -1)" webstats1:/home/ubuntu
#now root, then to switch to user ubuntu
# su - ubuntu

# to kill the server
# docker rm --force webstats1