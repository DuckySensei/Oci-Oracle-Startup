import oci
from oci.core import ComputeClient
from oci.core.models import LaunchInstanceDetails

config = oci.config.from_file('~/.oci/config')
compute_client = ComputeClient(config)

launch_instance_details = LaunchInstanceDetails()
launch_instance_details.compartment_id = 'COMPARTMENT_OCID'
launch_instance_details.shape = 'VM.Standard.E2.1.micro'
launch_instance_details.display_name = 'OCI-launchAPI'

response = compute_client.launch_instance(launch_instance_details)
instance_ocid = response.data.id

print('launched instance', instance_ocid)
