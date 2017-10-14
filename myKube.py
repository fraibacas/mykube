#!/usr/bin/env python

import argparse
import os
import subprocess
import time


MASTER = "kmaster"
WORKERS = [ "kworker1", "kworker2" ]
MASTER_IP = "192.168.33.10"

MASTER_SETUP  = '/usr/bin/sudo bash -c "kubeadm reset && kubeadm init --apiserver-advertise-address 192.168.33.10 --pod-network-cidr 10.244.0.0/16"'
WORKER_SETUP  = '/usr/bin/sudo bash -c "kubeadm reset && {}"'
NODE_TEARDOWN = '/usr/bin/sudo bash -c "kubeadm reset"'
JOIN_CMD_MATCHER = "kubeadm join --token"
CAT_KUBECTL_CONFIG = "sudo cat /etc/kubernetes/admin.conf"
CALICO_CMD = "kubectl apply -f https://docs.projectcalico.org/v2.6/getting-started/kubernetes/installation/hosted/kubeadm/1.6/calico.yaml"
WEAVE_CMD = "kubectl apply -f https://git.io/weave-kube-1.6"
# need to install an older version of the dashboard to get it to work without certs
#DASHBOARD_CMD = "kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml"
DASHBOARD_CMD = "kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.3/src/deploy/kubernetes-dashboard.yaml" 
DELETE_NODE_CMD = "kubectl delete node {}"
DRAIN_NODE_CMD = "kubectl drain {} --delete-local-data --force --ignore-daemonsets"
GET_NODES_CMD = "kubectl get nodes"
GET_PODS_CMD = "kubectl get pods --all-namespaces -o wide"

DASHBOARD_URL = "http://localhost:8001/api/v1/namespaces/kube-system/services/http:kubernetes-dashboard:/proxy"

JOIN_CMD_FILE = "./.join_cmd.txt"

# Grant super-user access to all service accounts cluster-wide (strongly discouraged)
BYPASS_RBAC_SVC_ACCOUNTS = "kubectl create clusterrolebinding serviceaccounts-cluster-admin --clusterrole=cluster-admin --group=system:serviceaccounts"

def execute_command(command, debug=False):
    """
    Params: command to execute
    Return: tuple containing the stout and stderr of the command execution
    """
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
        print_header("Setting up kubectl config...")
        # set kubectl config in master vm
        vm_command = "mkdir -p ~/.kube && {} > ~/.kube/config".format(CAT_KUBECTL_CONFIG)
        command = "vagrant ssh {} -c '{}'".format(self.master, vm_command)
        out, err = execute_command(command)
        # set kubectl config in local host
        execute_command("mkdir -p ~/.kube")
        out, err = self._run_in_master(CAT_KUBECTL_CONFIG)
        if "certificate-authority-data" in out:
            with open("{}/.kube/config".format(os.getenv("HOME")), "w") as f:
                f.write(out)
            print "Kubectl configured!"

    def _run_in_master(self, cmd):
        cmd = "vagrant ssh {} -c '{}'".format(self.master, cmd)
        return execute_command(cmd)

    def _install_calico(self):
        print_header("Configuring cluster network to use Calico")
        out, err = self._run_in_master(CALICO_CMD)

    def _install_weave(self):
        print_header("Configuring cluster network to use Weave")
        out, err = self._run_in_master(WEAVE_CMD)

    def _install_dashboard(self):
        # https://github.com/kubernetes/dashboard/wiki/Accessing-Dashboard---1.7.X-and-above
        # https://github.com/kubernetes/dashboard/wiki/Access-control#authorization-header
        # Use an older version of the dasboard to avoid issues
        # https://stackoverflow.com/questions/46411598/kubernetes-dashboard-serviceunavailable-503-error
        #
        print_header("Installing Kubernetes dashboard")
        out, err = self._run_in_master(DASHBOARD_CMD)
        print_yellow("Kubernetes Dashboard installed")
        print_yellow("To run it execute 'kubectl proxy' and go to {}".format(DASHBOARD_URL))

    def _bypass_rbac_for_service_accounts_for_now(self):
        print_header("Granting super-user access to all service accounts cluster-wide (strongly discouraged)")
        out, err = self._run_in_master(BYPASS_RBAC_SVC_ACCOUNTS)

    def start_master(self):
        join_cmd = self._start_master()
        time.sleep(5)
        if join_cmd:
            # update local kubectl config with the new master
            self._set_up_kubectl()
            # add calico
            self._install_calico()
            time.sleep(5)
            self._install_dashboard()
            self._bypass_rbac_for_service_accounts_for_now()
        # save the join cmd to a file
        with open(JOIN_CMD_FILE, "w") as f:
            f.write(join_cmd)
        return join_cmd

    def start_workers(self, join_cmd=None):
        if not join_cmd:
            with open(JOIN_CMD_FILE, "r") as f:
                join_cmd = f.read()
            self._start_workers(join_cmd)

    def start(self):
        # Start the master
        join_cmd = self.start_master()

        if join_cmd:
            self._start_workers(join_cmd)
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
        #for node in nodes:
        #    drain_cmd = DRAIN_NODE_CMD.format(node)
        #    delete_cmd = DELETE_NODE_CMD.format(node)
        #    out, err = execute_command("{} && {}".format(drain_cmd, delete_cmd))
        for node in nodes:
            out, err = execute_command("vagrant ssh {} -c '{}'".format(node, NODE_TEARDOWN))


def main(options):
    cluster = KubeCluster(MASTER, WORKERS)
    if options.action == "start-cluster":
        cluster.start()
    elif options.action in [ "stop-cluster", "stop" ]:
        cluster.stop()
    elif options.action == "start-master":
        cluster.start_master()
    elif options.action == "start-workers":
        cluster.start_workers()
    elif options.action == "checks":
        cluster.print_nodes()
        cluster.print_pods()


def parse_options():
    parser = argparse.ArgumentParser(description="Start/Stop a kubenetes cluster configured with vagrant", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("action", type=str, choices=['stop', 'stop-cluster', 'checks', "start-master", "start-workers"], help="Action to perform")
    return parser.parse_args()


if __name__ == "__main__":
    import sys
    options = parse_options()
    print("{} called with options {}\n".format(sys.argv[0], options))
    main(options)
