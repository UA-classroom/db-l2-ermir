@echo off
cd backend
call .venv\Scripts\activate

:: Här är ändringen: Vi skriver app.main istället för bara main
uvicorn app.main:app --reload

pause