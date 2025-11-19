#!/usr/bin/env python3
"""
Quick script to check and update .env file
"""
import os
from pathlib import Path

env_file = Path(".env")

if env_file.exists():
    print("Current .env file contents:")
    print("-" * 40)
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)
        print("-" * 40)
        
    # Check if it has the old model
    if "gpt-4-turbo-preview" in content:
        print("\n⚠️  WARNING: Found old model 'gpt-4-turbo-preview'")
        print("Please update OPENAI_MODEL to one of these:")
        print("  - gpt-4o-mini (recommended)")
        print("  - gpt-4o")
        print("  - gpt-3.5-turbo")
        print("\nEdit backend/.env and change:")
        print("  OPENAI_MODEL=gpt-4-turbo-preview")
        print("to:")
        print("  OPENAI_MODEL=gpt-4o-mini")
    else:
        print("\n✅ Model looks good!")
else:
    print("❌ .env file not found!")
    print("Create it by copying env.example:")
    print("  cp env.example .env")
    print("\nThen add your OPENAI_API_KEY and set OPENAI_MODEL=gpt-4o-mini")

