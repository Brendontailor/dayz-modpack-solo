@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =====================================================================
::  START DO SERVIDOR - DayZ 1.30 (solo / modpack)
::  A ordem dos mods NAO e mais automatica: ela vem do MODS.txt
::  Para ativar/desativar um mod, edite MODS.txt (linha com # = off).
:: =====================================================================

title Apocalipse - DayZ Server

set "serverName=Apocalipse"
:: usa a propria pasta do .bat (funciona de qualquer lugar, sem editar caminho)
set "serverLocation=%~dp0"
set "serverPort=2302"
set "serverConfig=serverDZ.cfg"
set "modsFile=MODS.txt"
set "serverCPU=4"
set "exThreads=7"
set "restartSeconds=43200"

cd /d "%serverLocation%" || (
    echo [ERRO] Nao foi possivel acessar %serverLocation%
    pause
    exit /b 1
)

if not exist "DayZServer_x64.exe" (
    echo [ERRO] DayZServer_x64.exe nao encontrado.
    pause
    exit /b 1
)
if not exist "%serverConfig%" (
    echo [ERRO] %serverConfig% nao encontrado.
    pause
    exit /b 1
)
if not exist "profiles" mkdir "profiles"

:start
set "clientMods="
set "modCount=0"
set "missingMods="

if not exist "%modsFile%" goto autodetect

echo.
echo (%time%) Lendo ordem de mods de %modsFile%...

for /f "usebackq tokens=* delims=" %%L in ("%modsFile%") do (
    set "line=%%L"
    if defined line (
        if not "!line:~0,1!"=="#" (
            if exist "!line!\" (
                if defined clientMods (
                    set "clientMods=!clientMods!;!line!"
                ) else (
                    set "clientMods=!line!"
                )
                set /a modCount+=1
            ) else (
                set "missingMods=!missingMods! !line!"
            )
        )
    )
)

if defined missingMods (
    echo [AVISO] Pastas listadas no MODS.txt mas ausentes no disco:
    echo         !missingMods!
)

if not defined clientMods goto autodetect
goto launch

:autodetect
echo.
echo (%time%) MODS.txt nao encontrado ou vazio - detectando pastas @* ...
for /d %%D in (@*) do (
    if exist "%%~fD\." (
        if defined clientMods (
            set "clientMods=!clientMods!;%%~nxD"
        ) else (
            set "clientMods=%%~nxD"
        )
        set /a modCount+=1
    )
)
if not defined clientMods (
    echo [ERRO] Nenhum mod encontrado.
    pause
    exit /b 1
)

:launch
echo (%time%) Mods carregados: !modCount!
echo (%time%) Iniciando %serverName% na porta %serverPort%...

start "DayZ Server" /min "DayZServer_x64.exe" -config=%serverConfig% -port=%serverPort% -profiles=profiles "-mod=!clientMods!" -cpuCount=%serverCPU% -exThreads=%exThreads% -maxMem=2047 -maxVRAM=2047 -dologs -adminlog -freezecheck

echo.
echo (%time%) Reinicio automatico em 12 horas ^(fecha com CTRL+C para parar^).
timeout /t %restartSeconds% /nobreak

taskkill /im DayZServer_x64.exe /F >nul 2>&1
timeout /t 5 /nobreak >nul
goto start
