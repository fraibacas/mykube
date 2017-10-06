# ----------------------------------------------------------------------------
# Resources:
#   https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/
#   http://blog.pichuang.com.tw/Installing-Kubernetes-on-Linux-with-kubeadm/
#   https://zihao.me/post/creating-a-kubernetes-cluster-from-scratch-with-kubeadm/
# ----------------------------------------------------------------------------

Vagrant.configure("2") do |config|

    # Worker 1
    #
    config.vm.define "kube-worker-1" do |worker|
        worker.vm.box = "ubuntu/xenial64"
        worker.vm.hostname = "kube-worker-1"
        worker.vm.box_url = "https://vagrantcloud.com/ubuntu/xenial64"

        worker.vm.network :private_network, ip: "10.10.10.11"

        worker.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--memory", 2048]
            v.customize ["modifyvm", :id, "--name", "kube-worker-1"]
            # Use faster paravirtualized networking
            v.customize ["modifyvm", :id, "--nictype1", "virtio"]
            v.customize ["modifyvm", :id, "--nictype2", "virtio"]
        end
        worker.vm.provision :shell, :path => "./provision.sh", :args => "'worker'"
    end

    # Worker 2
    #
    config.vm.define "kube-worker-2" do |worker|
        worker.vm.box = "ubuntu/xenial64"
        worker.vm.hostname = "kube-worker-2"
        worker.vm.box_url = "https://vagrantcloud.com/ubuntu/xenial64"

        worker.vm.network :private_network, ip: "10.10.10.12"

        worker.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--memory", 2048]
            v.customize ["modifyvm", :id, "--name", "kube-worker-2"]
            # Use faster paravirtualized networking
            v.customize ["modifyvm", :id, "--nictype1", "virtio"]
            v.customize ["modifyvm", :id, "--nictype2", "virtio"]
        end
        worker.vm.provision :shell, :path => "./provision.sh", :args => "'worker'"
    end

    # Kubernetes Master
    #
    config.vm.define "kube-master" do |master|
        master.vm.box = "ubuntu/xenial64"
        master.vm.hostname = 'kube-master'
        master.vm.box_url = "https://vagrantcloud.com/ubuntu/xenial64"

        master.vm.network :private_network, ip: "10.10.10.10"

        master.vm.provider :virtualbox do |v|
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--memory", 2048]
            v.customize ["modifyvm", :id, "--name", "kube-master"]
            # Use faster paravirtualized networking
            v.customize ["modifyvm", :id, "--nictype1", "virtio"]
            v.customize ["modifyvm", :id, "--nictype2", "virtio"]
        end
        master.vm.provision :shell, :path => "./provision.sh", :args => "'master'"
    end

end
