import boto3
import ipaddress
import random

class Subnets:
    def __init__(self, region='us-east-1'):
         self.region = region
         self.client = boto3.client('ec2', region)
         self.vpc_data = None
         
    def _random_subnet(self, prefix):
        self.prefix = prefix
        
        if not (8 <= prefix <= 30):
            raise ValueError("Prefix must be between 8 and 30")
        
        base_ip = '10.' + ".".join(str(random.randint(0, 254)) for _ in range(2)) + '.0'
        random_ip = ipaddress.IPv4Address(base_ip)
        
        subnet = ipaddress.IPv4Network(f"{random_ip}/{prefix}", strict=False)
        
        return subnet
    
    def subnet_check(self, prefix: int):
        self.prefix = prefix
        
        random_subnet = self._random_subnet(prefix)
        #client = boto3.client('ec2')
        current_subnets = self.client.describe_subnets()
        
        aws_subnets = []
        for subnet in current_subnets['Subnets']:
            aws_subnets.append(subnet['CidrBlock'])
        print(aws_subnets)
            
        for cidr in aws_subnets:
            cidr = ipaddress.IPv4Network(cidr)
            while cidr.overlaps(random_subnet):
                    random_subnet = self._new_subnet()
                    print(random_subnet)
                    random_subnet = ipaddress.IPv4Network(random_subnet, strict=False)
                    cidr.overlaps(random_subnet)
        return random_subnet
    
    def create_subnet(self, VpcId, CidrBlock, tag_name):
        self.VpcId = VpcId
        self.CidrBlock = CidrBlock
        self.tag_name = tag_name
        
        response = self.client.create_subnet(
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': tag_name
                        }
                    ]
                }
            ],
            CidrBlock = CidrBlock,
            VpcId = VpcId
        )
        
        rt = self.client.describe_route_tables()
        for i in rt['RouteTables']:
            if i['VpcId'] == VpcId:
                self.client.associate_route_table(
                    RouteTableId = i['RouteTableId'],
                    SubnetId = response['Subnet']['SubnetId']
                )
        
        return response