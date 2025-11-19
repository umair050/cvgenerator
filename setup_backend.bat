@echo off
echo Setting up CV Converter Backend...
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
echo Upgrading pip first...
python -m pip install --upgrade pip
echo Installing packages...
pip install -r requirements.txt

echo.
echo Backend setup complete!
echo.
echo Next steps:
echo 1. Copy env.example to .env
echo 2. Add your OPENAI_API_KEY to .env
echo 3. Run: uvicorn main:app --reload
echo.
pause

