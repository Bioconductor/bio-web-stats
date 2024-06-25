FROM ubuntu:latest

ENV container docker

RUN apt-get update && \
    apt-get install -y systemd systemd-sysv openssh-server apache2 sudo \
        python3 python3-pip python3.12-venv curl unzip nano vim tree && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and add to sudoers
RUN useradd -m -s /bin/bash webstats-user && \
    echo 'webstats-user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Enable the Apache service
RUN systemctl enable apache2

# Copy the Apache service file
COPY apache2.service /etc/systemd/system/multi-user.target.wants/

# Configure and enable SSH service
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN echo 'ubuntu:ubuntu' | chpasswd
RUN echo 'webstats-user:webstats-user' | chpasswd

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
RUN systemctl enable ssh

EXPOSE 22 80 5000

# Set the default command to run systemd
CMD ["/lib/systemd/systemd"]