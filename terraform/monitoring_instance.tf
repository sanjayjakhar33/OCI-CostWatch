resource "oci_core_vcn" "costwatch_vcn" {
  cidr_blocks    = ["10.10.0.0/16"]
  compartment_id = var.compartment_ocid
  display_name   = "costwatch-vcn"
  dns_label      = "costwatch"
}

resource "oci_core_subnet" "costwatch_subnet" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.costwatch_vcn.id
  cidr_block                 = "10.10.1.0/24"
  display_name               = "costwatch-subnet"
  dns_label                  = "monitor"
  prohibit_public_ip_on_vnic = false
}

resource "oci_core_network_security_group" "costwatch_nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.costwatch_vcn.id
  display_name   = "costwatch-nsg"
}

resource "oci_core_network_security_group_security_rule" "ingress_ssh" {
  network_security_group_id = oci_core_network_security_group.costwatch_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = "0.0.0.0/0"
  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_instance" "costwatch_monitor" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_ocid
  shape               = var.instance_shape
  display_name        = "oci-costwatch-monitor"

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_in_gbs
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.costwatch_subnet.id
    assign_public_ip = true
    nsg_ids          = [oci_core_network_security_group.costwatch_nsg.id]
  }

  source_details {
    source_type = "image"
    # Oracle Linux 8 image OCID placeholder; replace per region.
    source_id = "ocid1.image.oc1..replace_me"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(<<-EOF
      #!/bin/bash
      dnf -y update
      dnf -y install docker git
      systemctl enable --now docker
      usermod -aG docker opc
      EOF
    )
  }
}
