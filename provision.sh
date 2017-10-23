#!/bin/bash
export MASTER_IP=192.168.33.10
export NFS_FOLDER=/opt/kdata

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

apt-get update && apt-get install -y \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common  > /dev/null 2>&1

apt-get update && apt-get install -y docker-engine kubelet kubeadm kubectl kubernetes-cni > /dev/null 2>&1
apt-get install nfs-common -y  > /dev/null 2>&1

# create nfs folder
mkdir -p ${NFS_FOLDER}
chmod 777 ${NFS_FOLDER}

if [ $1 = "master" ]; then
    apt-get install -y nfs-kernel-server > /dev/null 2>&1
    echo "${NFS_FOLDER} *(rw,sync,no_root_squash)" >> /etc/exports
    systemctl restart nfs-kernel-server
else
    mount ${MASTER_IP}:${NFS_FOLDER} ${NFS_FOLDER}
    echo "${MASTER_IP}:${NFS_FOLDER} ${NFS_FOLDER} nfs rw,hard,intr 0 0" >> /etc/fstab
fi