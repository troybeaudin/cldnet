from .vpc import VPC
from .peer import Peer
import itertools
import yaml

def create_vpc(name=None, prefix_length=None):
    
    return VPC().new_vpc(name, prefix_length)

def standardize_vpc_peerings(yaml_file):
    peer = Peer()
           
    if yaml_file.split(".")[-1] not in ['yaml','yml']:
        raise TypeError("File must be a YAML")
    else:
        with open(yaml_file, "r") as file:
            vpc_peer = yaml.safe_load(file)
    
    vpcs = []
    for i in vpc_peer['VpcPeerings']:
        from_group = i['FromGroup']
        to_group = i['ToGroup']
        vpcs.append(list(set(vpc_peer['VpcGroups'][from_group] + vpc_peer['VpcGroups'][to_group])))
        
    peers = [peers for vpc in vpcs for peers in list(itertools.combinations(vpc,2))]
    
    for vpc in peers:
        vpc1 = vpc[0]
        vpc2 = vpc[1]
        
        peer.peering_vpcs(vpc1, vpc2)
        peer.peer_route(vpc1, vpc2)