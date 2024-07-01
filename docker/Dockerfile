FROM ubuntu:latest

ARG OSGROUP=webstats
ARG OSUSER=webstats

ENV OSGROUP=${OSGROUP}
ENV OSUSER=${OSUSER}
ENV container docker

RUN apt-get update && \
    apt-get install -y systemd systemd-sysv openssh-server apache2 sudo \
        python3 python3-pip python3.12-venv curl unzip nano vim tree && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Check if group exists, if not create it
RUN if getent group ${OSGROUP} >/dev/null; then \
        echo "Group ${OSGROUP} exists"; \
    else \
        groupadd ${OSGROUP}; \
    fi

RUN echo useradd -m -s /bin/bash -g ${OSGROUP} ${OSUSER} 
# Check if user exists, if not create it
RUN if id -u ${OSUSER} >/dev/null 2>&1; then \
        echo "User ${OSUSER} exists"; \
    else \
        useradd -m -s /bin/bash -g ${OSGROUP} ${OSUSER} --home /home/${OSUSER} && \
        echo "${OSUSER}:${OSUSER}" | chpasswd && \
        echo "${OSUSER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers; \
    fi

# Enable the Apache service
RUN systemctl enable apache2

# Copy the Apache service file
COPY apache2.service /etc/systemd/system/multi-user.target.wants/

# Configure and enable SSH service
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
RUN systemctl enable ssh

EXPOSE 22 80 5000

# Set the default command to run systemd
CMD ["/lib/systemd/systemd"]