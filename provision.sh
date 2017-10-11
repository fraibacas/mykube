#!/bin/bash

apt-get update && apt-get install -y \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common  > /dev/null 2>&1

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
apt-get update && apt-get install -y docker-engine kubelet kubeadm kubectl kubernetes-cni > /dev/null 2>&1

#if [ $1 = "master" ]; then
#fi