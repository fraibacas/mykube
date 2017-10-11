# -*- mode: ruby -*-
# vi: set ft=ruby :


# ----------------------------------------------------------------------------
# Resources:
#   https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/
#   http://blog.pichuang.com.tw/Installing-Kubernetes-on-Linux-with-kubeadm/
#   https://zihao.me/post/creating-a-kubernetes-cluster-from-scratch-with-kubeadm/
#   https://crondev.com/kubernetes-installation-kubeadm/
# ----------------------------------------------------------------------------


Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/xenial64"
    config.vm.box_url = "https://vagrantcloud.com/ubuntu/xenial64"

    check_guest_additions = false

    config.vm.provider "virtualbox" do |v|
        v.memory = 2048
        v.cpus = 2
    end

    config.vm.define "kmaster" do |node|
        node.vm.hostname = "kmaster"
        node.vm.network :private_network, ip: "192.168.33.10"
        node.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--name", "kmaster"]
        end
        node.vm.provision :shell, inline: "sed 's/127\.0\.0\.1.*kmaster.*/192\.168\.33\.10 kmaster/' -i /etc/hosts"
        node.vm.provision :shell, :path => "./provision.sh", :args => "'master'"
    end


    config.vm.define "kworker1" do |node|
        node.vm.hostname = "kworker1"
        node.vm.network :private_network, ip: "192.168.33.20"
        node.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--name", "kworker1"]
        end
        node.vm.provision :shell, inline: "sed 's/127\.0\.0\.1.*kworker1.*/192\.168\.33\.20 kworker1/' -i /etc/hosts"
        node.vm.provision :shell, :path => "./provision.sh", :args => "'worker'"
    end

    config.vm.define "kworker2" do |node|
        node.vm.hostname = "kworker2"
        node.vm.network :private_network, ip: "192.168.33.30"
        node.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--name", "kworker2"]
        end
        node.vm.provision :shell, inline: "sed 's/127\.0\.0\.1.*kworker2.*/192\.168\.33\.30 kworker2/' -i /etc/hosts"
        node.vm.provision :shell, :path => "./provision.sh", :args => "'worker'"
    end
end
