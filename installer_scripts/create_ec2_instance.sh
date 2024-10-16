#!/bin/bash
# A script to create a stand-alone EC2 instance for webstats

# The profile_ID for the aws crednetials
PROFILE_ID=bioc
# Allocate an Elastic IP (uncomment if you haven't allocated one yet)
# EIP_ALLOCATION_ID=$(aws --profile=$PROFILE_ID ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
# or uncomment the line below one if we already ahve an EIP
EIP_ALLOCATION_ID="eipalloc-09836615eabe474d9"  # Replace with your Elastic IP allocation ID

# TODO MOdify creation so that EIP will survive termination of Instance
# Parameterize the Name tag value
INSTANCE_NAME="bioc-webstats-server4"  # Replace with your desired instance name

# Generate a unique client token
CLIENT_TOKEN=$(uuidgen)

# TODO Attch the correct role
# Launch the EC2 instance
INSTANCE_ID=$(aws --profile=$PROFILE_ID ec2 run-instances --image-id "ami-04b70fa74e45c3917" --instance-type "t3.small" --instance-initiated-shutdown-behavior "stop" --key-name "rshear-2023-07" --block-device-mappings '{"DeviceName":"/dev/sda1","Ebs":{"Encrypted":false,"DeleteOnTermination":false,"Iops":3000,"VolumeSize":10,"VolumeType":"gp3","Throughput":125}}' --network-interfaces '{"SubnetId":"subnet-8bd210a0","DeleteOnTermination":true,"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-0c1a550c794f7f48e","sg-06d862363ca409a55"]}' --hibernation-options '{"Configured":false}' --monitoring '{"Enabled":true}' --credit-specification '{"CpuCredits":"unlimited"}' --capacity-reservation-specification '{"CapacityReservationPreference":"open"}' --tag-specifications "ResourceType=instance,Tags=[{Key=bioc:notes,Value='This server delivers content to www.bioconductor.org/packages/stats/ via reverse-proxy to master.'},{Key=bioc:application,Value=webstats},{Key=Name,Value=$INSTANCE_NAME},{Key=bioc:availability,Value=high},{Key=bioc:creator,Value=robert.shear@bioconductor},{Key=bioc:environment,Value=production}]" --iam-instance-profile '{"Arn":"arn:aws:iam::555219204010:instance-profile/AmazonSSMRoleForInstancesQuickSetup"}' --enclave-options '{"Enabled":false}' --metadata-options '{"HttpEndpoint":"enabled","HttpProtocolIpv6":"disabled","HttpPutResponseHopLimit":1,"HttpTokens":"optional","InstanceMetadataTags":"disabled"}' --placement '{"Tenancy":"default"}' --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":false,"EnableResourceNameDnsAAAARecord":false}' --maintenance-options '{"AutoRecovery":"default"}' --client-token "$CLIENT_TOKEN" --count "1" --query 'Instances[0].InstanceId' --output text)

# Wait for the instance to be in running state
aws --profile=$PROFILE_ID ec2 wait instance-running --instance-ids $INSTANCE_ID

# associate bioc-webstats-runner instance profile with instance
# TODO this assumes that the iip is already defined
aws --profile=$PROFILE_ID ec2 replace-iam-instance-profile-association --association-id "iip-assoc-05817f9302900b693" --iam-instance-profile '{"Arn":"arn:aws:iam::555219204010:instance-profile/bioc-webstats-webrunner","Name":"bioc-webstats-webrunner"}' 

# Associate the Elastic IP with the instance
aws --profile=$PROFILE_ID ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $EIP_ALLOCATION_ID

echo "Instance $INSTANCE_ID is created and Elastic IP associated with the name $INSTANCE_NAME."