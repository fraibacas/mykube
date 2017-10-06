
import argparse
import os
import subprocess


MASTER = "kube-master"
WORKERS = [ "kube-worker-1", "kube-worker-2" ]


MASTER_SETUP  = '/usr/bin/sudo bash -c "kubeadm reset && kubeadm init --pod-network-cidr 10.10.10.0/24 --service-cidr 10.96.0.0/12 --service-dns-domain \"zing.loc\" --apiserver-advertise-address 10.10.10.10"'
WORKER_SETUP  = '/usr/bin/sudo bash -c "kubeadm reset && {}"'
NODE_TEARDOWN = '/usr/bin/sudo bash -c "kubeadm reset"'
JOIN_CMD_MATCHER = "kubeadm join --token"
CAT_KUBECTL_CONFIG = "sudo cat /etc/kubernetes/admin.conf"
CALICO_CMD = "kubectl apply -f http://docs.projectcalico.org/v2.3/getting-started/kubernetes/installation/hosted/kubeadm/1.6/calico.yaml"
DELETE_NODE_CMD = "kubectl delete node {}"
DRAIN_NODE_CMD = "kubectl drain {} --delete-local-data --force --ignore-daemonsets"
GET_NODES_CMD = "kubectl get nodes"
GET_PODS_CMD = "kubectl get pods --all-namespaces"

def execute_command(command, debug=True):
    """
    Params: command to execute
    Return: tuple containing the stout and stderr of the command execution
    """
    if debug:
        print 'Executing ....' + command
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if debug:
        print_command_output(stdout, stderr)
    return (stdout, stderr)


def print_command_output(out, err):
    print " Stdout: {}".format(out)
    print "--"
    print " Stderr: {}".format(err)


class BColors:
    HEADER = '\033[95m'
    BLUE = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(msg):
    print "{}{}{}".format(BColors.HEADER, msg, BColors.ENDC)


def print_yellow(msg):
    print "{}{}{}".format(BColors.YELLOW, msg, BColors.ENDC)


def print_red(msg):
    print "{}{}{}".format(BColors.RED, msg, BColors.ENDC)


class KubeCluster(object):
    def __init__(self, master, workers):
        self.master = master
        self.workers = workers

    def _get_join_cmd(self, output):
        cmd = None
        if output:
            for line in output.split("\n"):
                if JOIN_CMD_MATCHER in line:
                    cmd = line.strip()
                    break
        return cmd

    def _start_master(self):
        print_header("Initializing Kubernetes master...")
        command = "vagrant ssh {} -c '{}'".format(self.master, MASTER_SETUP)
        out, err = execute_command(command)
        join_cmd = self._get_join_cmd(out)
        if not join_cmd:
            print "Error: Master did not properly initialized"
            print_command_output(out, err)
        return join_cmd

    def _start_workers(self, join_cmd):
        print_header("Initializing Kubernetes workers...")
        for worker in self.workers:
            worker_cmd = WORKER_SETUP.format(join_cmd)
            command = "vagrant ssh {} -c '{}'".format(worker, worker_cmd)
            out, err = execute_command(command)

    def _set_up_kubectl(self):
        """
        Copy the kubectl config in the local machine from the master
        """
        print_header("Setting up kubectl config in your system...")
        command = "vagrant ssh {} -c '{}'".format(self.master, CAT_KUBECTL_CONFIG)
        out, err = execute_command(command)
        if "certificate-authority-data" in out:
            with open("{}/.kube/config".format(os.getenv("HOME")), "w") as f:
                f.write(out)
            print "Kubectl configured!"

    def _install_calico(self):
        print_header("Configuring cluster network to use Calico")
        out, err = execute_command(CALICO_CMD)

    def start(self):
        # Start the master
        join_cmd = self._start_master()
        if join_cmd:
            # update local kubectl config with the new master
            self._set_up_kubectl()
            # get the workers to join the master
            self._start_workers(join_cmd)
            # add calico
            self._install_calico()
            # current issues:
                # - calico pods CrashLoopBackOff
                # kube-dns fails first time
                    # kubectl scale deployment --replicas=1 kube-dns --namespace=kube-system
            self.print_nodes()
            self.print_pods()

    def print_nodes(self):
        out, err = execute_command(GET_NODES_CMD, debug=False)
        print_header(out)

    def print_pods(self):
        out, err = execute_command(GET_PODS_CMD, debug=False)
        print_header(out)

    def stop(self):
        print_header("Stopping cluster...")
        nodes = [ self.master ]
        nodes.extend(self.workers)
        for node in nodes:
            drain_cmd = DRAIN_NODE_CMD.format(node)
            delete_cmd = DELETE_NODE_CMD.format(node)
            out, err = execute_command("{} && {}".format(drain_cmd, delete_cmd))
        for node in nodes:
            out, err = execute_command("vagrant ssh {} -c '{}'".format(node, NODE_TEARDOWN))


def main(options):
    cluster = KubeCluster(MASTER, WORKERS)
    if options.action == "start-cluster":
        cluster.start()
    elif options.action == "stop-cluster":
        cluster.stop()
    elif options.action == "checks":
        cluster.print_nodes()
        cluster.print_pods()


def parse_options():
    parser = argparse.ArgumentParser(description="Start/Stop a kubenetes cluster configured with vagrant", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("action", type=str, choices=['start-cluster', 'stop-cluster', 'checks'], help="Action to perform")
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    options = parse_options()
    print("{} called with options {}\n".format(sys.argv[0], options))
    main(options)

