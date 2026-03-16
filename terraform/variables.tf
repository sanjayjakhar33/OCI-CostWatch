variable "tenancy_ocid" { type = string }
variable "user_ocid" { type = string }
variable "fingerprint" { type = string }
variable "private_key_path" { type = string }
variable "region" { type = string }
variable "compartment_ocid" { type = string }
variable "availability_domain" { type = string }
variable "instance_shape" { type = string  default = "VM.Standard.E4.Flex" }
variable "instance_ocpus" { type = number default = 1 }
variable "instance_memory_in_gbs" { type = number default = 8 }
variable "ssh_public_key" { type = string }
