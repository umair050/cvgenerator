# How to Run the Backend

## For Git Bash / Linux / Mac Users

### Step 1: Activate Virtual Environment

**In Git Bash:**
```bash
source venv/Scripts/activate
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 2: Run the Server

```bash
uvicorn main:app --reload
```

---

## For Windows CMD / PowerShell Users

### Step 1: Activate Virtual Environment

**In CMD:**
```cmd
venv\Scripts\activate
```

**In PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

### Step 2: Run the Server

```bash
uvicorn main:app --reload
```

---

## Troubleshooting

### "uvicorn: command not found"

**Solution:** Make sure the virtual environment is activated!

1. Check if you see `(venv)` in your prompt
2. If not, activate it using the commands above
3. Verify uvicorn is installed: `pip list | grep uvicorn`
4. If not installed: `pip install uvicorn`

### "source: command not found" (Windows CMD)

**Solution:** Use the Windows activation script instead:
```cmd
venv\Scripts\activate.bat
```

### Virtual environment not found

**Solution:** Create it first:
```bash
python -m venv venv
```

Then activate it using the appropriate command for your shell.

---

## Quick Check

Run these commands to verify everything is set up:

```bash
# Check Python version
python --version

# Check if venv is activated (should show venv path)
which python

# Check if uvicorn is installed
pip show uvicorn

# List all installed packages
pip list
```

