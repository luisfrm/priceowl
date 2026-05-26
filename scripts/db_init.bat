@echo off
echo Inicializando carpeta de migraciones...
uv run flask --app server.app db init
pause
