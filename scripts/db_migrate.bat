@echo off
set /p msg="Ingresa la descripcion de la migracion: "
echo Generando migracion: %msg%...
uv run flask --app server.app db migrate -m "%msg%"
pause
