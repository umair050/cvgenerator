# Quick Start Guide - CV Converter

## 🚀 Quick Setup (Windows)

### Option 1: Using Setup Scripts (Easiest)

#### Step 1: Setup Backend
1. Double-click `setup_backend.bat` or run it from command prompt
2. This will:
   - Create a virtual environment
   - Install all Python dependencies
   - Show you next steps

#### Step 2: Configure OpenAI API Key
1. Navigate to `backend` folder
2. Copy `env.example` to `.env`:
   ```bash
   copy env.example .env
   ```
3. Open `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```
   > **Get your API key from**: https://platform.openai.com/api-keys

#### Step 3: Setup Frontend
1. Double-click `setup_frontend.bat` or run it from command prompt
2. This will install all Node.js dependencies

---

## 🏃 Running the Application

### Terminal 1: Start Backend Server

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ Backend is running at: **http://localhost:8000**

### Terminal 2: Start Frontend Server

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

✅ Frontend is running at: **http://localhost:3000**

---

## 📝 Manual Setup (If scripts don't work)

### Backend Setup

1. **Open Command Prompt or PowerShell**

2. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

4. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```
   (You should see `(venv)` in your prompt)

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Create .env file:**
   ```bash
   copy env.example .env
   ```

7. **Edit .env file** and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

8. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Open a NEW Command Prompt or PowerShell**

2. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

---

## ✅ Verify Installation

### Check Backend:
- Open browser: http://localhost:8000
- You should see: `{"message":"CV Converter API is running"}`
- Check formats: http://localhost:8000/api/formats

### Check Frontend:
- Open browser: http://localhost:3000
- You should see the CV Converter interface

---

## 🎯 Using the Application

1. **Open** http://localhost:3000 in your browser
2. **Upload** a CV file (PDF or DOCX)
3. **Select** a format (e.g., "Datamatics Professional")
4. **Optionally** add custom instructions
5. **Click** "Convert CV"
6. **Download** your formatted CV

---

## ⚠️ Troubleshooting

### Backend Issues:

**Problem: `python` command not found**
- Solution: Install Python 3.8+ from python.org
- Or use `py` instead of `python` on Windows

**Problem: `uvicorn` command not found**
- Solution: Make sure virtual environment is activated
- Run: `pip install -r requirements.txt` again

**Problem: OpenAI API error**
- Solution: Check your `.env` file has correct API key
- Verify API key is valid at https://platform.openai.com/api-keys
- Make sure you have credits in your OpenAI account

**Problem: Port 8000 already in use**
- Solution: Change port: `uvicorn main:app --reload --port 8001`
- Update frontend `vite.config.js` to point to new port

### Frontend Issues:

**Problem: `npm` command not found**
- Solution: Install Node.js 16+ from nodejs.org

**Problem: Port 3000 already in use**
- Solution: Vite will automatically use next available port
- Or specify: `npm run dev -- --port 3001`

**Problem: Cannot connect to backend**
- Solution: Make sure backend is running on port 8000
- Check CORS settings in `backend/main.py`

---

## 🔧 Prerequisites Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] OpenAI API key obtained
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] `.env` file configured with API key

---

## 📞 Need Help?

1. Check the main `README.md` for detailed information
2. Verify all prerequisites are installed
3. Check that both servers are running
4. Review error messages in terminal windows
5. Ensure `.env` file is properly configured

---

## 🎉 You're Ready!

Once both servers are running, open http://localhost:3000 and start converting CVs!

