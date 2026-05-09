#!/bin/bash
echo "Initiating Jetson Voxel Tier Hydration..."
git pull origin main
git lfs pull
echo "Verifying TensorRT Engines..."
for f in models/*.engine; do
    [ -e "$f" ] && echo "Found: $f" || echo "ERROR: Missing Binary Weights"
done
