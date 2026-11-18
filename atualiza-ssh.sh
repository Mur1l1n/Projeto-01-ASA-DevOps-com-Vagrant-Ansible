#!/usr/bin/env bash

for vm in arq app db cli; do
  host="$vm.murilo.rian.devops"
  printf '\n=== %s ===\n' "$host"
  ssh-keygen -R "$host"
  ssh -o StrictHostKeyChecking=ask -o HostKeyAlgorithms=ssh-ed25519 \
    -o PubkeyAuthentication=no -o PasswordAuthentication=no \
    -o KbdInteractiveAuthentication=no "vagrant@$host"
done