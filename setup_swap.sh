#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./setup_swap.sh)"
  exit 1
fi

echo "Checking for existing swap..."
swapon --show

if [ $(swapon --show | wc -l) -gt 0 ]; then
    echo "Swap already exists. Skipping creation."
    exit 0
fi

echo "Creating 4GB swap file..."
fallocate -l 4G /swapfile

echo "Setting permissions..."
chmod 600 /swapfile

echo "Formatting swap file..."
mkswap /swapfile

echo "Enabling swap..."
swapon /swapfile

echo "Making swap permanent in /etc/fstab..."
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

echo "Swap created successfully!"
swapon --show
free -h
