FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG TARGETARCH

ENV container=docker
STOPSIGNAL SIGRTMIN+3

# Update package index and install required base packages
RUN apt-get update && \
    apt-get install -y systemd systemd-sysv ca-certificates wget gnupg software-properties-common g++ freeglut3-dev build-essential libx11-dev libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev python3.10 python3.10-venv python3.10-dev openssh-server tigervnc-standalone-server tigervnc-xorg-extension tigervnc-viewer xorg xfce4 dbus-x11 sudo git curl nano tmux ffmpeg htop vlc x11-xserver-utils xfce4-terminal dbus snapd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done) && \
    rm -f /lib/systemd/system/multi-user.target.wants/* && \
    rm -f /etc/systemd/system/*.wants/* && \
    rm -f /lib/systemd/system/local-fs.target.wants/* && \
    rm -f /lib/systemd/system/sockets.target.wants/*udev* && \
    rm -f /lib/systemd/system/sockets.target.wants/*initctl* && \
    rm -f /lib/systemd/system/basic.target.wants/* && \
    rm -f /lib/systemd/system/anaconda.target.wants/* && \
    find /etc/systemd/system /lib/systemd/system -path '*.wants/*' -exec rm {} \; && \
    echo 'tmpfs /run tmpfs mode=755,nosuid,nodev 0 0' > /etc/fstab && \
    echo 'tmpfs /tmp tmpfs mode=1777,nosuid,nodev 0 0' >> /etc/fstab

# Generate machine-id
RUN systemd-machine-id-setup

# Add OBS Studio repository (works for both architectures)
RUN add-apt-repository -y ppa:obsproject/obs-studio && \
    apt-get update && \
    apt-get install -y obs-studio && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Conditional Google Chrome installation based on architecture
RUN if [ "$TARGETARCH" = "amd64" ]; then \
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb; \
    else \
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_arm64.deb -O chrome.deb; \
    fi && \
    apt-get update && \
    apt-get install -y ./chrome.deb || apt-get install -f -y && \
    rm chrome.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Conditional VS Code installation based on architecture
RUN if [ "$TARGETARCH" = "amd64" ]; then \
        wget -q https://update.code.visualstudio.com/latest/linux-deb-x64/stable -O vscode.deb; \
    else \
        wget -q https://update.code.visualstudio.com/latest/linux-deb-arm64/stable -O vscode.deb; \
    fi && \
    apt-get update && \
    dpkg -i vscode.deb || apt-get install -f -y && \
    rm vscode.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure SSH and logging
RUN sed -i 's/#Port 22/Port 22/g' /etc/ssh/sshd_config && \
    mkdir /var/run/sshd && \
    sed -i 's/Storage=auto/Storage=persistent/' /etc/systemd/journald.conf

# Install snapd
RUN apt-get update && \
    apt-get install -y snapd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV USER="" \
    PASSWORD="" \
    VNCPASSWORD=""

# Copy entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose necessary ports
EXPOSE 22 5901 3389

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
