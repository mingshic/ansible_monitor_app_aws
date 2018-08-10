---


- name: Create the VPC
  ec2_vpc:
    state: present
    ec2_access_key: '{{ ec2_access_key }}'
    ec2_secret_key: '{{ ec2_secret_key }}'
    dns_support: true
    dns_hostnames: true
    resource_tags: '{{ resource_tags_vpc }}'
    cidr_block: "{{ cidr_block }}"
    subnets: 
      - cidr: "{{ item.subnets_cidr }}"
        az: '{{ item.subnets_az }}'
        resource_tags: '{{ item.resource_tags_subnets }}'
    internet_gateway: true
    route_tables: 
      - subnets: 
        - "{{ item.subnets_cidr }}"
        routes:
        - dest: 0.0.0.0/0
          gw: igw
    region: '{{ region }}'
  register: "{{ item.register }}"
  with_items: "{{ vpc_subnets }}"
  tags:
    - create_vpc
  
- set_fact: vpc_id={{ "{{ item.register }}".vpc_id }}
  tags:
    - create_vpc

- name: security group set
  ec2_group:
    name: vpc-web
    description: an web for test
    ec2_access_key: '{{ ec2_access_key }}'
    ec2_secret_key: '{{ ec2_secret_key }}'
    vpc_id: "{{ vpc_id }}"
    rules:
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        from_port: 22
        to_port: 22
        cidr_ip: 0.0.0.0/0
      - proto: icmp
        from_port: -1
        to_port: -1
        cidr_ip: 0.0.0.0/0
    region: '{{ region }}'
  tags:
    - create_vpc
    - ec2_group

- name: delete VPC
  ec2_vpc:
    state: absent
    ec2_access_key: '{{ ec2_access_key }}'
    ec2_secret_key: '{{ ec2_secret_key }}'
    resource_tags: '{{ resource_tags_vpc }}'
    vpc_id: '{{ delete_vpc_id }}'
    region: '{{ region }}'
  tags:
    - delete_vpc

- name: Get the ubuntu trusty AMI
  ec2_ami_search: 
    distro: '{{ distro }}'
    release: '{{ release }}'
    virt: '{{ virt }}'
    region: '{{ region }}'
  register: image_ami
  tags:
    - create_ec2

- name: start the ec2 instance
  ec2:
    image: "{{ image_ami.ami }}"
    region: '{{ region }}'
    ec2_access_key: '{{ ec2_access_key }}'
    ec2_secret_key: '{{ ec2_secret_key }}'
    instance_type: '{{ instance_type }}'
    assign_public_ip: true
    key_name: '{{ pair_key_name }}'
    group: '{{ security_group_name }}'
    instance_tags: '{{ resource_tags_instance_ec2 }}'
    exact_count: '{{ instance_number }}'
    count_tag: '{{ count_tag }}'
    vpc_subnet_id: '{{ vpc_subnet_id }}'
#    wait: 'yes'
  register: ec2
  tags:
    - create_ec2
