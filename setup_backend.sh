#!/bin/bash
# Setup script for Git Bash / Linux / Mac

echo "Setting up CV Converter Backend..."
cd backend

echo "Creating virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

echo "Upgrading pip first..."
python -m pip install --upgrade pip

echo "Installing packages..."
pip install -r requirements.txt

echo ""
echo "Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy env.example to .env"
echo "2. Add your OPENAI_API_KEY to .env"
echo "3. Run: source venv/Scripts/activate (or venv/bin/activate on Linux/Mac)"
echo "4. Run: uvicorn main:app --reload"
echo ""

