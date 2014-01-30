from kamaki.cli.config import Config
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.cyclades import CycladesClient
from kamaki.clients.network import NetworkClient


class SynnefoResolver(object):
    def __init__(self, logger, cloud=None):
        self.logger = logger
        kamaki_config = Config()
        self.clouds = dict(kamaki_config.items("cloud"))
        if not self.clouds:
            raise RuntimeError("No available clouds to connect")
        if cloud is not None:
            if cloud not in self.clouds:
                raise ValueError("Unknown cloud '%s'" % cloud)
            self.clouds = dict([(k, v) for k, v in self.clouds.items()
                               if k == cloud])

    def resolve(self, server_name):
        # Get the server cloud if any
        server_name, server_cloud = parse_server_name(server_name)

        if server_cloud is None:
            lookup_clouds = self.clouds.keys()
        else:
            lookup_clouds = [server_cloud]

        for cloud_name in lookup_clouds:
            cloud_info = self.clouds.get(cloud_name)
            if cloud_info is None:
                raise ValueError("Unknown cloud '%s'" % cloud_name)
            url = cloud_info["url"]
            token = cloud_info["token"]
            self.logger.debug("Looking up server '%s' to cloud '%s'",
                              server_name, cloud_name)
            ssh_info = self._resolve(url, token, server_name, cloud_name)
            if ssh_info is not None:
                return ssh_info
        return None

    def _resolve(self, auth_url, auth_token, server_name, cloud_name):
        client = self.get_server_client(auth_url, auth_token)

        server_id = None
        # Find the ID of the server
        for server in client.list_servers(detail=False):
            if server["name"] == server_name:
                server_id = server["id"]
                break
        else:  # Server not found
            return None

        server_details = client.get_server_details(server_id)

        server_fqdn = server_details.get("SNF:fqdn")
        port_forwarding = get_server_ssh_port_forwarding(server_details)
        server_nics = server_details["attachments"]

        if len(server_nics) == 0:
            return []

        public_networks = self.get_public_networks(auth_url, auth_token)

        for nic in server_nics:
            if nic["ipv4"] and nic["network_id"] in public_networks:
                ipv4_address = nic["ipv4"]
                break
        else:
            ipv4_address = None

        for nic in server_nics:
            if nic["ipv6"] and nic["network_id"] in public_networks:
                ipv6_address = nic["ipv6"]
                break
        else:
            ipv6_address = None

        # Find the user from the server metadata
        server_metadata = server_details["metadata"]
        user = server_metadata.get("users")

        ssh_info = {
            "name": server_name,
            "cloud": cloud_name,
            "user": user,
            "fqdn": server_fqdn,
            "ipv4": ipv4_address,
            "ipv6": ipv6_address,
            "port_forwarding": port_forwarding,
        }
        return ssh_info

    def list_servers(self, cloud_name=None):
        servers = {}
        clouds = [cloud_name] if cloud_name is not None else self.clouds.keys()
        for cloud_name in clouds:
            cloud_info = self.clouds.get(cloud_name)
            if cloud_info is None:
                raise ValueError("Unknown cloud '%s'" % cloud_name)
            url = cloud_info["url"]
            token = cloud_info["token"]
            client = self.get_server_client(url, token)
            cloud_servers = client.list_servers(detail=False)
            servers[cloud_name] = [s["name"] for s in cloud_servers]
        return servers

    def get_public_networks(self, auth_url, auth_token):
        client = self.get_network_client(auth_url, auth_token)
        networks = client.list_networks()
        return [net["id"] for net in networks if net["public"]]

    def get_server_client(self, auth_url, auth_token):
        astakos_client = self.get_astakos_client(auth_url, auth_token)
        servers_url = \
            astakos_client.get_service_endpoints("compute")["publicURL"]
        return CycladesClient(servers_url, auth_token)

    def get_network_client(self, auth_url, auth_token):
        astakos_client = self.get_astakos_client(auth_url, auth_token)
        networks_url = \
            astakos_client.get_service_endpoints("network")["publicURL"]
        return NetworkClient(networks_url, auth_token)

    def get_astakos_client(self, auth_url, auth_token):
        return AstakosClient(auth_url, auth_token)


def get_server_ssh_port_forwarding(server):
    pf = server.get("SNF:port_forwarding")
    if pf is not None:
        return pf.get("22")
    else:
        return None


def parse_server_name(server_name):
    if "." in server_name:
        server_name, server_domain = server_name.split(".", 1)
        return (server_name, server_domain)
    else:
        return (server_name, None)
