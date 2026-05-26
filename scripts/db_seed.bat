@echo off
echo Sembrando datos en la base de datos...
uv run flask --app server.app seed-db
pause
