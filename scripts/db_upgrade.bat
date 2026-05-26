@echo off
echo Aplicando migraciones a la base de datos...
uv run flask --app server.app db upgrade
pause
