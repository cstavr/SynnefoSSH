from synnefo_ssh import client


class SynnefoResolver(object):
    def __init__(self, logger, cloud=None):
        self.cloud = cloud
        self.client = client.SynnefoClient(cloud)

    def resolve(self, server_name):
        server_id = None
        # Find the ID of the server
        for server in self.client.compute.list_servers(detail=False):
            if server["name"] == server_name:
                server_id = server["id"]
                break
        else:  # Server not found
            return None

        server_details = self.client.compute.get_server_details(server_id)

        server_fqdn = server_details.get("SNF:fqdn")
        port_forwarding = get_server_ssh_port_forwarding(server_details)
        server_nics = server_details["attachments"]

        if len(server_nics) == 0:
            return []

        public_networks = self.get_public_networks()

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
            "cloud": self.cloud,
            "user": user,
            "fqdn": server_fqdn,
            "ipv4": ipv4_address,
            "ipv6": ipv6_address,
            "port_forwarding": port_forwarding,
        }
        return ssh_info

    def get_public_networks(self):
        networks = self.client.network.list_networks()
        return [net["id"] for net in networks if net["public"]]


def get_server_ssh_port_forwarding(server):
    pf = server.get("SNF:port_forwarding")
    if pf is not None:
        return pf.get("22")
    else:
        return None
