
import subprocess
import requests
import unittest
import json
from collections import defaultdict

EDGE = "edge"
GW_SERVICE = "traefik-web-ui"
SVC_TIER = [ "model-ingest", "authorization" ]
BACK_TIER = [ "data-pipeline" ]

SERVICES = SVC_TIER + [ EDGE ] + [ GW_SERVICE ]

MASTER_IP = "192.168.33.10"

ALLOWED = { EDGE:           [ GW_SERVICE ],
            GW_SERVICE:       SVC_TIER + [ EDGE ],
}
for svc in SVC_TIER:
    ALLOWED[svc] = SVC_TIER + [ GW_SERVICE ]


class PodTypes(object):
    EDGE_POD = "edge"
    GW_POD   = "gw_service"
    SVC_TIER_PODS = [ "model-ingest", "data-pipeline", "authorization" ]
    ALL_PODS = SVC_TIER_PODS + [ EDGE_POD ] + [ GW_POD ]
    ALLOWED_CONNECTIONS = {
        EDGE_POD:  [ GW_POD ],
        GW_POD:    SVC_TIER_PODS + [EDGE_POD]
    }
    for pod_type in SVC_TIER_PODS:
        ALLOWED_CONNECTIONS[pod_type] = SVC_TIER_PODS + [ GW_POD ]


def execute_command(command, debug=False):
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


def get_edge_port():
    out, _ = execute_command('kubectl get svc edge -o json | jq ".spec.ports[0].nodePort"')
    edge_port = int(out.strip())
    print "Edge port {}".format(edge_port)
    return edge_port


class Pod(object):
    def __init__(self, name, ip):
        self.name = name
        self.pod_type = "-".join(name.split("-")[:-2])
        self.ip = ip
        self.port = "80"
        if PodTypes.GW_POD in name:
            self.port = "8080"


class PodNetworkTests(unittest.TestCase):

    EDGE_PORT_ATTR = "edge_port_attr"

    @classmethod
    def setUpClass(cls):
        setattr(cls, cls.EDGE_PORT_ATTR, get_edge_port())

    @property
    def edge_port(self):
        return getattr(self, self.EDGE_PORT_ATTR, None)

    def test_requests_through_edge(self):
        self.assertTrue(self.edge_port)
        for svc in SVC_TIER:
            url = "http://{}:{}/api/{}".format(MASTER_IP, self.edge_port, svc)
            resp = requests.get(url, timeout=5)
            self.assertTrue(resp.ok)
            self.assertTrue(svc in resp.content)
            print "\033[95m{} is reachable via Edge.\033[0m".format(svc)

    def _get_pod_and_check(self, from_svc, to_svc):
        pod = from_svc
        if from_svc == GW_SERVICE:
            pod = "traefik-ingress-controller"
        output_check = to_svc
        if to_svc == GW_SERVICE:
            output_check = 'href="/dashboard/">Found'
        elif to_svc == EDGE:
            output_check = "Welcome to nginx!"
        return pod, output_check

    def _get_pods(self):
        pods = {}
        cmd = "kubectl get pods -o json"
        out, err = execute_command(cmd)
        pod_data = json.loads(out)
        for pod in pod_data.get("items", []):
            name = pod["metadata"]["name"]
            ip = pod["status"]["podIP"]
            pods[name] = Pod(name, ip)
        return pods

    def pod_connectivity(self, policies_installed=False):
        """ Checks all pods can connect to all other pods """
        pods = self._get_pods()
        pod_names = pods.keys()
        pod_names.sort()
        for from_pod_name in pod_names:
            for to_pod_name in pod_names:
                to_pod = pods[to_pod_name]
                from_pod = pods[from_pod_name]
                # cant run kubectl from the traefik pod
                #if from_pod.pod_type == PodTypes.GW_POD:
                #    continue
                cmd = "kubectl exec -it {} -- ping -c 1 -w 1 {}".format(from_pod_name, to_pod.ip)
                out, err = execute_command(cmd)
                success = False
                if "1 packets received," in out:
                    success = True
                color = '\033[95m' if success else '\033[91m'
                print "{}{} => {}\033[0m      {}".format(color, from_pod_name, to_pod_name, cmd)
                
        """
        for from_svc in SERVICES:
            for to_svc in SERVICES:
                if from_svc == to_svc or from_svc == GW_SERVICE:
                    # traefik image does not have curl or any tool we can use to test connectivity
                    continue
                pod_grep, output_check = self._get_pod_and_check(from_svc, to_svc)
                # get pods running svc
                cmd = "kubectl get pods | grep {}".format(pod_grep) + " |  awk '{print $1}'"
                out, _ = execute_command(cmd)
                for pod in out.split("\n"):
                    pod = pod.strip()
                    if pod:
                        should_succeed = False
                        if not policies_installed or to_svc in ALLOWED[from_svc]:
                            should_succeed = True
                        #if not should_succeed:
                        #import pdb; pdb.set_trace()
                        curl_cmd = "curl -m 5 {}:80".format(to_svc)
                        cmd = "kubectl exec -it {} -- {}".format(pod, curl_cmd)
                        out, err = execute_command(cmd)
                        connectivity = '\033[95m'
                        if "Connection timed out" in out:
                            connectivity = '\033[91m'
                        self.assertTrue(out)
                        #self.assertTrue(output_check in out)
                        print "{}{}({}) => {}\033[0m".format(connectivity, from_svc, pod, to_svc)
                        print "\t-------------------"
                        print "\t{}".format(cmd)
                        print "\t{}".format(out)
                        print "\t{}".format(err)
                        print "\t-------------------"
        """


    def test_pod_connectivity(self):
        """ Checks pod connectivity """
        cmd = "kubectl get networkpolicies -o json"
        out, _ = execute_command(cmd)
        policies = json.loads(out)
        if len(policies["items"]):
            self.pod_connectivity(policies_installed=True)
        else:
            self.pod_connectivity(policies_installed=False)


if __name__ == "__main__":
    unittest.main()