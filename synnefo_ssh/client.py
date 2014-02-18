from kamaki.clients.cyclades import CycladesClient
from kamaki.clients.astakos import AstakosClient
from kamaki.clients.network import NetworkClient
from kamaki.clients.image import ImageClient

from synnefo_ssh import utils


class SynnefoClient(object):
    """Synnefo Client

    Wrapper class around clients of kamaki's clients for various Synnefo
    services:

    * astakos: Astakos client
    * compute: Cyclades Compute client
    * network: Cyclades Network client
    * image:   Cyclades Plankton client

    """
    def __init__(self, cloud=None, auth_url=None, token=None):
        if cloud is not None:
            auth_url, token = utils.get_cloud_credentials(cloud)
        self.auth_url, self.token = auth_url, token
        self.astakos = AstakosClient(self.auth_url, self.token)
        self.endpoints = self.get_api_endpoints()
        self.compute = CycladesClient(self.endpoints["cyclades_compute"],
                                      token)
        self.network = NetworkClient(self.endpoints["cyclades_network"], token)
        self.image = ImageClient(self.endpoints["cyclades_plankton"], token)

    def get_api_endpoints(self):
        """Get service endpoints from Astakos"""
        _endpoints = self.astakos.get_endpoints()["access"]
        endpoints = {}
        for service in _endpoints["serviceCatalog"]:
            endpoints[service["name"]] = service["endpoints"][0]["publicURL"]
        return endpoints
