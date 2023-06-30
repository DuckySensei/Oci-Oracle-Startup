''' Example using Python OCI (oracle cloud infrastructure) api to list all instances in a compartment '''
import oci # OCI Python SDK (pip install oci

# Function: get_instances
def get_instances(config, compartment_id):
    ''' Get all instances in a compartment '''
    # Create ComputeClient
    compute_client = oci.core.compute_client.ComputeClient(config)
    # Get all instances in a compartment
    instances = compute_client.list_instances(compartment_id)
    # Return instances
    return instances


# Set up oci.config object to use for connection
config = oci.config.from_file() # Use default OCI config file (mac ~/.oci/config)

# Validate config
oci.config.validate_config(config)

# Shows Object Storage
object_storage_client = oci.object_storage.ObjectStorageClient(oci.config.from_file())
result = object_storage_client.get_namespace()
print("Current object storage namespace: {}\n".format(result.data))

# Getcompartment id
compartment_id = config["tenancy"]

identity = oci.identity.IdentityClient(config)
u = identity.list_users(compartment_id)
print(u.data)