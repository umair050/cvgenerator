#!/bin/bash
# Fix for Rust compilation issues - installs packages with pre-built wheels

echo "Upgrading pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

echo ""
echo "Installing packages (this may take a few minutes)..."
pip install --only-binary :all: -r requirements.txt

echo ""
echo "If that fails, trying without --only-binary flag..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "Verify with: pip list"

