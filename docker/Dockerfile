FROM ubuntu:latest

ENV container docker

RUN apt-get update && \
    apt-get install -y systemd systemd-sysv openssh-server && \
    systemctl enable ssh

VOLUME [ "/sys/fs/cgroup" ]

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

STOPSIGNAL SIGRTMIN+3

EXPOSE 22
EXPOSE 5000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
