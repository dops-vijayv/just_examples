import sys
from getopt import getopt, GetoptError
from boto3 import session

#######################################################################
# AWSPROFILEFILE is the aws profile file you've predefined in local
# CSVEXPORTFILE: the file name you want the ec2 records to
# be exported to in csv format.
#######################################################################
AWSPROFILEFILE = ''
CSVEXPORTFILE = ''

#######################################################################
# The below takes the CLI arguments and prints the script usage.
#######################################################################
try:
    OPTIONS, ARGS = getopt(sys.argv[1:], "i:o:")
except GetoptError as err:
    print(str(err))
    print("Usage: %s -i input_AWSPROFILEFILE -o CSVEXPORTFILE-to-export" % sys.argv[0])
    sys.exit(2)

for o, a in OPTIONS:
    if o == '-i':
        AWSPROFILEFILE = a
    elif o == '-o':
        CSVEXPORTFILE = a

#######################################################################
# OPENS a new session for the given profile
#######################################################################
AWS_SESSION = session.Session(profile_name=AWSPROFILEFILE)

EXPORT_OUTPUT = sys.stdout
FILEOPEN = open(CSVEXPORTFILE, 'w')
sys.stdout = FILEOPEN
COLUMNHEADER = '["InstanceId", "InstanceType", "ImageId", "State.Name", "LaunchTime", ' \
               '"Placement.AvailabilityZone", "Placement.Tenancy", "PrivateIpAddress",' \
               '"PrivateDnsName", "PublicDnsName", "Name"]'
FIELDS = ','.join(COLUMNHEADER)
#######################################################################
# The below print adds the column header in the CSV Export File
#######################################################################
print(FIELDS)

CLIENT = AWS_SESSION.client('ec2')
#######################################################################
# EC2 Client is A low-level client representing Amazon Elastic Compute
# Cloud (EC2).
# Filters is used to fetch instances that belong to a specific VPC and
# the running instances.
#######################################################################
DATA_RESPONSE = CLIENT.describe_instances(
    Filters=[{
        'Name': 'instance-state-name',
        'Values': ['running']
    }, {
        'Name': 'vpc-id',
        'Values': ['#profileid'] #Can be passed dynamically if required
    }]
)

#######################################################################
# DATA_RESPONSE is the list of response we get for each instances.
# EACH is the list of each instance records.
# TAG is the TAG name given for each instances.
#######################################################################
for RECORD in DATA_RESPONSE['Reservations']:
    for EACH in RECORD['Instances']:
        for TAG in EACH['Tags']:
            if TAG['Key'] == 'Name':
                FIELD_DATA = (RECORD['InstanceId'], RECORD['InstanceType'], RECORD['ImageId'], RECORD['State']['Name'], RECORD['LaunchTime'], RECORD['Placement']['AvailabilityZone'], RECORD['Placement']['Tenancy'], RECORD['PrivateIpAddress'], RECORD['PrivateDnsName'], RECORD['PublicDnsName'], TAG['Value'])
                print(*FIELD_DATA, sep=",")
sys.stdout = EXPORT_OUTPUT
FILEOPEN.close()
