# Installation Troubleshooting Guide

## Rust Compilation Error

If you encounter errors about Rust/Cargo not being installed, here are solutions:

### Solution 1: Use Standard Uvicorn (Recommended - Already Applied)

The `requirements.txt` has been updated to use `uvicorn` without `[standard]` extra, which avoids Rust dependencies.

**Try installing again:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Solution 2: Install Pre-built Wheels

Sometimes pip needs to be upgraded to find pre-built wheels:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Solution 3: Use Alternative PDF Parser (If pdfplumber fails)

If `pdfplumber` still causes issues, you can use PyPDF2 instead:

1. Install alternative requirements:
   ```bash
   pip install -r requirements-no-rust.txt
   ```

2. Update `backend/services/cv_parser.py` to use PyPDF2:
   ```python
   # Change from:
   import pdfplumber
   
   # To:
   import PyPDF2
   ```

3. Update the `_parse_pdf` method accordingly.

### Solution 4: Install Rust (If you want full performance)

If you want the performance benefits of `uvicorn[standard]`:

1. Install Rust from: https://rustup.rs/
2. Restart your terminal
3. Use the original requirements:
   ```bash
   pip install uvicorn[standard]
   ```

## Common Issues

### Issue: "pip is not recognized"
- **Solution**: Make sure Python is installed and added to PATH
- Or use: `python -m pip` instead of `pip`

### Issue: "Microsoft Visual C++ 14.0 or greater is required"
- **Solution**: Install Visual Studio Build Tools from Microsoft
- Or use pre-built wheels (Solution 2 above)

### Issue: "Failed building wheel"
- **Solution**: Upgrade pip, setuptools, and wheel first
- Then try installing again

## Verify Installation

After installation, verify all packages are installed:

```bash
pip list
```

You should see:
- fastapi
- uvicorn
- openai
- pdfplumber (or PyPDF2)
- python-docx
- pydantic
- python-dotenv

## Still Having Issues?

1. Make sure you're using Python 3.8 or higher
2. Make sure virtual environment is activated
3. Try installing packages one by one to identify the problematic package
4. Check Python version: `python --version`
5. Check pip version: `pip --version`

