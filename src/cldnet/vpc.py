from .subnets import Subnets
from .peer import Peer
import boto3
from botocore.exceptions import ClientError

class VPC:    
    def __init__(self, region='us-east-1'):
         self.region = region
         self.client = boto3.client('ec2', region)
         self.peer = Peer()
         self.subs = Subnets()
         self.VpcId = None
               
    def new_vpc(self, tag_name: str, prefix_length: int, account=None, region='us-east-1'):
        self.tag_name = tag_name
        self.prefix_length = prefix_length
        
        new_cidr = self.subs.subnet_check(prefix_length)
        try:
            response = self.client.create_vpc(
                CidrBlock=str(new_cidr),
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
            
            self.subs.create_subnet(self.VpcId, str(new_cidr), tag_name)
        
            return self
            
        except ClientError as e:
            print(f"Error: {e}")
             
    def peer_to(self, other_vpc):
        self.other_vpc = other_vpc
        
        self.peer.peering_vpcs(other_vpc.VpcId, self.VpcId)
        self.peer.peer_route(other_vpc.VpcId, self.VpcId)
            
    