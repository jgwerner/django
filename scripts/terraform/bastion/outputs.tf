// Bastion external IP address.
output "external_ip" {
  value = "${aws_eip.bastion.public_ip}"
}