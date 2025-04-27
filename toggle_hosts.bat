@echo off
:: Check for Admin rights
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting Administrator permission...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~f0 %*' -Verb RunAs"
    exit /b
)

setlocal enabledelayedexpansion
set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
set ENTRY=127.0.0.1    api-esp32-smarthome.local

if "%1"=="on" (
    echo Enabling entry...
    powershell -command "(Get-Content '%HOSTS_FILE%') -replace '^# 127\.0\.0\.1\s+api-esp32-smarthome\.local', '127.0.0.1    api-esp32-smarthome.local' | Set-Content '%HOSTS_FILE%' -Force"
    goto :eof
)

if "%1"=="off" (
    echo Disabling entry...
    powershell -command "(Get-Content '%HOSTS_FILE%') -replace '^127\.0\.0\.1\s+api-esp32-smarthome\.local', '# 127.0.0.1    api-esp32-smarthome.local' | Set-Content '%HOSTS_FILE%' -Force"
    goto :eof
)

echo Usage: %0 [on|off]
pause
