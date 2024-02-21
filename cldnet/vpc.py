import boto3
import yaml
import itertools
from .subnets import Subnets
from .peer import Peer

class VPC:    
    def __init__(self, region='us-east-1'):
         self.region = region
         self.client = boto3.client('ec2', region)
         self.peer = Peer()
         self.subs = Subnets()
         self.VpcId = None
               
    def create_vpc(self, tag_name: str, prefix_length: int, account=None, region='us-east-1'):
        self.tag_name = tag_name
        self.prefix_length = prefix_length
        self.account = account
        self.region = region
        
        new_vpc = self.subs.subnet_check(prefix_length)
        response = self.client.create_vpc(
            CidrBlock=str(new_vpc),
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags':[
                        {
                            'Key': 'Name',
                            'Value': tag_name
                            }
                        ]
                    }
                ]
            )
        
        self.VpcId = response['Vpc']['VpcId']
        
        self.subs.create_subnet(self.VpcId, str(new_vpc), tag_name)
        
        return self
             
    def peer_to(self, other_vpc):
        self.other_vpc = other_vpc
        
        self.peer.peering_vpcs(other_vpc.VpcId, self.VpcId)
        self.peer.peer_route(other_vpc.VpcId, self.VpcId)

    @staticmethod  
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
            
        #vpcs = list(itertools.combinations(vpcs, 2))
        
        #new = [new for i in vpcs for new in list(itertools.combinations(i,2))]
        peers = [peers for vpc in vpcs for peers in list(itertools.combinations(vpc,2))]
        
        for vpc in peers:
            vpc1 = vpc[0]
            vpc2 = vpc[1]
            
            peer.peering_vpcs(vpc1, vpc2)
            peer.peer_route(vpc1, vpc2)
            