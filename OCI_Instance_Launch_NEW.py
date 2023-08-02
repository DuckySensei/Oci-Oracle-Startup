import oci
import os.path
import sys

OPERATING_SYSTEM = 'Oracle Linux'
config = oci.config.from_file()

def get_shape(compute_client, compartment_id, availability_domain):
    list_shapes_response = oci.pagination.list_call_get_all_results(
        compute_client.list_shapes,
        compartment_id,
        availability_domain=availability_domain.name
    )
    shapes = list_shapes_response.data
    if len(shapes) == 0:
        raise RuntimeError('No shapes found')
    
    vm_shapes = list(filter(lambda shape: shape.shape.startswith("VM.Standard"), shapes))
    if len(vm_shapes) == 0:
            raise RuntimeError('No VM shape found')
    
    print('Found Shape: {}'.format (vm_shapes[0].shape))
    shape = vm_shapes[0]

    return shape

def create_subnet(virtual_network_composite_operations, vcn, availability_domain):
    subnet_name = 'py_sdk_example_subnet'
    create_subnet_details = oci.core.models.CreateSubnetDetails(
        compartment_id=vcn.compartment_id,
        availability_domain=availability_domain.name,
        display_name=subnet_name,
        vcn_id=vcn.id,
        cidr_block=vcn.cidr_block
    )
    create_subnet_response = virtual_network_composite_operations.create_subnet_and_wait_for_state(
        create_subnet_details,
        wait_for_states=[oci.core.models.Subnet.LIFECYCLE_STATE_AVAILABLE]
    )
    subnet = create_subnet_response.data

    print('Created Subnet: {}'.format(subnet.id))

    return subnet

def get_launch_instance_details(compartment_id, availability_domain, shape, image, subnet, ssh_public_key):
    instance_metadata = {
        'ssh_authorized_keys': ssh_public_key,
        'some_metadata_item': 'some_item_value'
    }
    instance_metadata['user_data'] = oci.util.file_content_as_launch_instance_user_data(
        './user_data.sh'
    )
    instance_name = 'Dylans lil instance :)'
    instance_source_via_image_details = oci.core.models.InstanceSourceViaImageDetails(
        image_id=image.id
    )
    create_vnic_details = oci.core.models.CreateVnicDetails(
        subnet_id=subnet.id
    )
    launch_instance_details = oci.core.models.LaunchInstanceDetails(
        display_name=instance_name,
        compartment_id=compartment_id,
        availability_domain=availability_domain.name,
        shape=shape.shape,
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus = 1,
            memory_in_gbs=2,
        ),
        metadata=instance_metadata,
        #extended_metadata=instance_extended_metadata,
        source_details=instance_source_via_image_details,
        create_vnic_details=create_vnic_details
    )
    return launch_instance_details


def launch_instance(compute_client_composite_operations, launch_instance_details):
    launch_instance_response = compute_client_composite_operations.launch_instance_and_wait_for_state(
        launch_instance_details,
        wait_for_states=[oci.core.models.Instance.LIFECYCLE_STATE_RUNNING]
    )
    instance = launch_instance_response.data

    print('Launched Instance: {}'.format(instance.id))
    print('{}'.format(instance))
    print()

    return instance

if __name__ == "__main__":
    if len(sys.argv) != 1:
        raise RuntimeError('Should be structured python [FILE_NAME]')
    
    compartment_id = config["tenancy"]
    cidr_block = "10.0.0.0/24"
    if os.path.isfile(os.path.expanduser('~/.ssh/id_rsa.pub')):
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
            ssh_public_key = f.read()
    
    identity_client = oci.identity.IdentityClient(config)
    compute_client = oci.core.ComputeClient(config)
    compute_client_composite_operations = oci.core.ComputeClientCompositeOperations(compute_client)
    virtual_network_client = oci.core.VirtualNetworkClient(config)
    virtual_network_composite_operations = oci.core.VirtualNetworkClientCompositeOperations(virtual_network_client)
    work_request_client = oci.work_requests.WorkRequestClient(config)

    list_availability_domain = oci.pagination.list_call_get_all_results(
        identity_client.list_availability_domains,
        compartment_id
    )
    availability_domain = list_availability_domain.data[0]

    #SHAPE
    shape = get_shape(compute_client, compartment_id, availability_domain)

    #IMAGES
    image = oci.pagination.list_call_get_all_results(
        compute_client.list_images,
        compartment_id,
        operating_system=OPERATING_SYSTEM,
        shape=shape.shape
    )
    images = image.data
    if len(images) == 0: raise RuntimeError ("No image found")
    image = images[0]
    print('Found Images: {}'.format(image.id))

    vcn = None
    subnet = None
    internet_gateway = None
    network_security_group = None
    instance = None
    instance_via_work_requests = None
    instance_with_network_security_group = None

    try:
        #VCN DETAILS
        vcn_details = oci.core.models.CreateVcnDetails(
            cidr_block=cidr_block,
            display_name = "Test VCN",
            compartment_id = compartment_id
        )
        vcn_response = virtual_network_composite_operations.create_vcn_and_wait_for_state(
            vcn_details,
            wait_for_states=[oci.core.models.Vcn.LIFECYCLE_STATE_AVAILABLE]
        )
        vcn = vcn_response.data
        print('Created VCN: {}'.format(vcn.id))

        #SUBNET DETAILS
        subnet = create_subnet(virtual_network_composite_operations, vcn, availability_domain)

        #INTERNET_GATEWAY
        # internet_gateway_details = oci.core.models.CreateInternetGatewayDetails(
        #     display_name='Test IG',
        #     compartment_id=vcn.compartment_id,
        #     is_enabled=True,
        #     vcn_id=vcn.id
        # )
        # internet_gateway_response = virtual_network_composite_operations.create_internet_gateway_and_wait_for_state(
        #     internet_gateway_details,
        #     wait_for_states=[oci.core.models.InternetGateway.LIFECYCLE_STATE_AVAILABLE]
        # )
        # internet_gateway = internet_gateway_response.data
        # print('Created internet gateway: {}'.format(internet_gateway.id))

        #ROUTE RULE
        # route_rule = oci.core.models.RouteRule(
        #      cidr_block = None,
        #      destination = '0.0.0.0/0',
        #      destination_type='CIDR_BLOCK',
        #      network_entity_id=internet_gateway.id
        # )
        # route_rule.append(route_rule)
        # route_table_details = oci.core.models.UpdateRouteTableDetails(route_rule=route_rule)
        # route_table_response = virtual_network_composite_operations.update_route_table_and_wait_for_state(
        #      vcn.default_route_table_id,
        #      route_table_details,
        #      wait_for_states=[oci.core.models.RouteTable.LIFECYCLE_STATE_AVAILABLE]
        # )
        # route_table = route_table_response.data
        # print('Updated Route Rules For VCN {}'.format(route_table.route_rules))
        
        # NETWORK SECURITY GROUP


        # NETWORK SECURITY RULES


        #LAUNCH INSTANCE DETAILS
        launch_instance_details = get_launch_instance_details(
            compartment_id, availability_domain, shape, image, subnet, ssh_public_key
        )

        #LAUNCH INSTANCE
        instance_response = compute_client_composite_operations.launch_instance_and_wait_for_state(
            launch_instance_details,
            wait_for_states=[oci.core.models.Instance.LIFECYCLE_STATE_RUNNING]
        )
        instance = launch_instance_details.data
        print('Launched Instance: {}'.format(instance.id))
        

    finally:
        if instance:
              compute_client_composite_operations.terminate_instance_and_wait_for_state(
                   instance.id,
                   wait_for_states=[oci.core.models.Instance.LIFECYCLE_STATE_TERMINATED]
              )

              print('Terminated Instance: {}'.format(instance.id))

        # if internet_gateway:
        #     route_table_details = oci.core.models.UpdateRouteTableDetails(route_rules=[])
        #     virtual_network_composite_operations.update_route_table_and_wait_for_state(
        #          vcn.default_route_table_id,
        #          route_table_details,
        #          wait_for_states=[oci.core.models.RouteTable.LIFECYCLE_STATE_AVAILABLE]
        #     )
            
        #     virtual_network_composite_operations.delete_internet_gateway_and_wait_for_state(
        #         internet_gateway.id,
        #         wait_for_states=[oci.core.models.InternetGateway.LIFECYCLE_STATE_TERMINATED]
        #     )

        if subnet:
             virtual_network_composite_operations.delete_subnet_and_wait_for_state(
                subnet.id,
                wait_for_states=[oci.core.models.Subnet.LIFECYCLE_STATE_TERMINATED]
             )

        if vcn:
            virtual_network_composite_operations.delete_vcn_and_wait_for_state(
                 vcn.id,
                 wait_for_states=[oci.core.models.Vcn.LIFECYCLE_STATE_TERMINATED]
            )