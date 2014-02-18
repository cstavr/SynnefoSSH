from kamaki.cli.config import Config

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
