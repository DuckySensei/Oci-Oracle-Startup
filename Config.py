import oci
from oci.config import from_file

config = from_file()

config = from_file(profile_name="integ-beta")

config = from_file(file_location="~/.oci/config.prod")
config = oci.config.from_file( "~/.oci/config","integ-beta-profile")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
print(user)
{
  "compartment_id": "ocid1.tenancy.oc1...",
  "description": "Integration testing user [BETA]",
  "id": "ocid1.user.oc1...",
  "inactive_status": "",
  "lifecycle_state": "ACTIVE",
  "name": "testing+integ-beta@corp.com",
  "time_created": "2016-08-30T23:46:44.680000+00:00"
}

config = {
    "user" : "-- my config",
    "key_file" : "~\Users\dmant\OneDrive\Documents\mykey.ppk",
    "fingerprint" : "my finger print",
    "tenancy" : "my config",
    "region" : "US Midwest (Chicago)"
}

from oci.config import validate_config
validate_config(config)
