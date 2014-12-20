from kamaki.cli.config import Config
import tabulate

if Config().getboolean('global', 'ignore_ssl'):
    try:
        from kamaki.clients.utils import https
        https.patch_ignore_ssl()
    except:
        pass


def get_cloud_names():
    return [cloud[0] for cloud in Config().items("cloud")]


def get_cloud_credentials(cloud_name):
    """Get cloud credentials from kamaki configuration file."""
    cloud = dict(Config().items("cloud")).get(cloud_name)
    if cloud is None:
        raise ValueError("Kamaki config file does not contain '%s' cloud." %
                         cloud_name)
    return cloud["url"], cloud["token"]


def get_server_cloud(server_name):
    """Get the server cloud from the server name."""
    if "." in server_name:
        server_name, server_domain = server_name.split(".", 1)
        return (server_name, server_domain)
    else:
        return (server_name, None)


def pretty_print_servers(client, server_ids=None):
    servers = client.compute.list_servers(detail=True)
    # volumes = client.volume.list_volumes(detail=True)
    ports = client.network.list_ports()
    if server_ids is not None:
        servers = [s for s in servers if s["id"] in server_ids]
    for s in servers:
        s["ports"] = [p for p in ports if int(p["device_id"]) == int(s["id"])]
        # s["volumes"] = [v for v in volumes if v["server_id"] == s["id"]]
    _servers = []
    for s in servers:
        s_id = s["id"]
        s_name = s["name"]
        state = s["status"]
        ips = [p["fixed_ips"][0]["ip_address"] for p in s["ports"]
               if p["fixed_ips"]
               and ":" not in p["fixed_ips"][0]["ip_address"]]
        ips = ",".join(ips)
        _servers.append((s_id, s_name, state, ips))
    print tabulate.tabulate(_servers)
