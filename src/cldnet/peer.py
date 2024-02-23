from .subnets import Subnets
import boto3
from botocore.exceptions import ClientError

class Peer:    
    def __init__(self, region='us-east-1'):
         self.region = region
         self.client = boto3.client('ec2', region)
         self.peer_data = None
         
         
    def peering_vpcs(self, vpc1_id, vpc2_id):
        self.vpc1_id = vpc1_id
        self.vpc2_id = vpc2_id
        
        new_peer = self.client.create_vpc_peering_connection(
            PeerVpcId=vpc1_id,
            VpcId=vpc2_id
        )
        
        try:
            self.client.accept_vpc_peering_connection(
                VpcPeeringConnectionId=new_peer['VpcPeeringConnection']['VpcPeeringConnectionId']
        )
        except ClientError as e:
            print(f"Error: {e}. Retrying to peer.")
            self.client.accept_vpc_peering_connection(
                VpcPeeringConnectionId=new_peer['VpcPeeringConnection']['VpcPeeringConnectionId']
            )
        
        self.peer_data = new_peer
        
        return new_peer
        
    def peer_route(self, vpc1, vpc2):
        self.vpc1 = vpc1
        self.vpc2 = vpc2
        
        vpcs = [vpc1,vpc2]
        
        for i in vpcs:
            if i == vpc1:
                dest_cidr = self._vpc_subnet_cidr(vpc2)
                vpc = vpc1
            else:
                dest_cidr = self._vpc_subnet_cidr(vpc1)
                vpc = vpc2
            self.client.create_route(
                DestinationCidrBlock = dest_cidr,
                VpcPeeringConnectionId = self.peer_data['VpcPeeringConnection']['VpcPeeringConnectionId'],
                RouteTableId = self._route_table_id(vpc)
            )
        
    def _route_table_id(self, VpcId):
        self.VpcId = VpcId
        
        rt = self.client.describe_route_tables()
        for i in rt['RouteTables']:
            if i['VpcId'] == VpcId:
                rt_id = i['RouteTableId']
                
        return rt_id
  
    def _vpc_subnet_cidr(self, VpcId):
        self.VpcId = VpcId
        
        vpc = self.client.describe_vpcs()
        for i in vpc['Vpcs']:
            if VpcId == i['VpcId']:
                sub_id = i['CidrBlock']
                
        return sub_id
        