# CldNet (CloudNet)
Python Module for creating, managing, and peering AWS VPC's

This module will create VPCs based on the name and prefix length provided. It will randomly create a subnet range based on the prefix length provided in the RFC1918 internal 10/8 range. It will ensure the chosen range does not overlap with an existing range. If you create multiple subnets, you can then peer them. Larger scale and existing VPC peering can be accomplished through a yaml file.

# About
I had attended an AWS re:invent conference a few years back and an important AWS speaker had showcased their internal Python module that would spin up VPCs with minimal information that would allow them to deploy across multiple environments and VPCs. This is my take on their highlights.

This was before Transit Gateway was widely available as a service. I recommend that service for production or larger scale deployments.

# Installation
Requires Python3 and [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation)

```
pip install -r requirements.txt
```

# Usage
Using the downloaded code, import the module
```
import cldnet
```
To create VPCs, where the name of the VPC being created and the subnet prefix length is specified
```
vpc0 = cldnet.create_vpc('vpc0', 24)
vpc1 = cldnet.create_vpc('vpc1', 24)
```
To peer the VPCs created
```
vpc0.peer_to(vpc1)
```
For existing or large scale VPC peerings
```
cldnet.standardize_vpc_peerings('peer.yaml')
```
With the YAML specified using this setup
```
---
VpcGroups:
  UsWest2FullMesh:
    - vpc-11111
    - vpc-22222
    - vpc-33333
  UsEast1FullMesh:
    - vpc-44444
    - vpc-55555
    - vpc-66666

VpcPeerings:
- FromGroup: UsEast1FullMesh
  ToGroup: UsEast1FullMesh
- FromGroup: UsWest2FullMesh
  ToGroup: UsWest2FullMesh
```