@echo off
chcp 65001 > nul
echo ===================================================
echo   PyForge: Мгновенный онлайн-доступ через туннель
echo ===================================================
echo.
echo 1. Запуск локального сервера PyForge в фоне...
start /b python run.py
timeout /t 2 > nul
echo.
echo 2. Создание защищенной публичной ссылки (SSH Tunnel)...
echo Ваша ссылка появится ниже (скопируйте ее в браузер):
echo.
ssh -R 80:localhost:8000 localhost.run
pause
