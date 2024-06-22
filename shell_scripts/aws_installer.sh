#!/bin/bash

# Function to install AWS CLI
install_aws_cli() {
  local url=$1
  local file=$2

  curl "$url" -o "$file"
  unzip "$file"
  sudo ./aws/install
  rm -rf aws "$file"
}

# Detect the operating system and architecture
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Linux)
    if [ "$ARCH" == "x86_64" ]; then
      URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
      FILE="awscliv2-linux-x86_64.zip"
    elif [ "$ARCH" == "aarch64" ]; then
      URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
      FILE="awscliv2-linux-aarch64.zip"
    else
      echo "Unsupported architecture: $ARCH"
      exit 1
    fi
    ;;
  Darwin)
    URL="https://awscli.amazonaws.com/AWSCLIV2.pkg"
    FILE="AWSCLIV2.pkg"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

# Install AWS CLI
if [ "$OS" == "Darwin" ]; then
  curl "$URL" -o "$FILE"
  sudo installer -pkg "$FILE" -target /
  rm "$FILE"
else
  install_aws_cli "$URL" "$FILE"
fi

# Verify installation
aws --version

echo "AWS CLI installation completed."
