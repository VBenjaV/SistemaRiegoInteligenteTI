@echo off
cd /d C:\Users\benja\Desktop\InfraTIGrupo2\SistemaRiegoInteligenteTI\backend
py -m uvicorn main:app --reload --port 8000
pause
