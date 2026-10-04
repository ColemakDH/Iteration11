#!/bin/bash
# Tests whether the SSH key's comment field is reflected/evaluated by the portal
ssh-keygen -t ed25519 -C '{{printf "%#v" .Vault}}' -f /tmp/testkey -N ""
echo "Key generated. Connecting..."
script -q ssh_keytest.log -c "ssh -p 2223 -i /tmp/testkey -o IdentitiesOnly=yes -l anyname 192.168.11.224"
