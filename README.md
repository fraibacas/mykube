# mykube
Creates a 3 node (master + 2 workers) kubernetes cluster in VirtualBox using Vagrant

Tested on VirtualBox 5.1.28 and Vagrant 2.0

kubectl should be manually installed in the host machine (https://kubernetes.io/docs/tasks/tools/install-kubectl)

Start cluster:

```
1) Create vms:
    vagrant up

2) Start Kubernetes master:
    python myKube.py start-master

3) Wait until all master pods are ready. To check status:
    kubectl get pods --all-namespaces -o wide

4) Start worker nodes:
    python myKube.py start-workers
```

Stop cluster:

```
python mykube.py stop-cluster
```

Check that all nodes were successfully added:

```
dev:~/mykube$ kubectl get nodes
NAME       STATUS    ROLES     AGE       VERSION
kmaster    Ready     master    5m        v1.8.0
kworker1   Ready     <none>    1m        v1.8.0
kworker2   Ready     <none>    1m        v1.8.0
```

Check all pods are running:

```
dev:~/mykube$ kubectl get pods --all-namespaces -o wide
NAMESPACE     NAME                                       READY     STATUS    RESTARTS   AGE       IP              NODE
kube-system   calico-etcd-ftflb                          1/1       Running   0          4m        192.168.33.10   kmaster
kube-system   calico-kube-controllers-6ff88bf6d4-m4bm7   1/1       Running   0          4m        192.168.33.10   kmaster
kube-system   calico-node-7f2pm                          2/2       Running   0          4m        192.168.33.10   kmaster
kube-system   calico-node-mtcnn                          2/2       Running   1          1m        192.168.33.20   kworker1
kube-system   calico-node-pnfdn                          2/2       Running   0          1m        192.168.33.30   kworker2
kube-system   etcd-kmaster                               1/1       Running   0          3m        192.168.33.10   kmaster
kube-system   kube-apiserver-kmaster                     1/1       Running   0          4m        192.168.33.10   kmaster
kube-system   kube-controller-manager-kmaster            1/1       Running   0          3m        192.168.33.10   kmaster
kube-system   kube-dns-545bc4bfd4-k25tz                  3/3       Running   0          4m        192.168.189.1   kmaster
kube-system   kube-proxy-5ztjb                           1/1       Running   0          1m        192.168.33.20   kworker1
kube-system   kube-proxy-9fk9m                           1/1       Running   0          4m        192.168.33.10   kmaster
kube-system   kube-proxy-tzsjg                           1/1       Running   0          1m        192.168.33.30   kworker2
kube-system   kube-scheduler-kmaster                     1/1       Running   0          3m        192.168.33.10   kmaster
```