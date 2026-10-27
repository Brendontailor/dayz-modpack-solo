@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =====================================================================
::  PLAY - inicia o CLIENTE do DayZ com os MESMOS mods do servidor
::
::  Le o MODS.txt e passa cada pasta como caminho absoluto em -mod=.
::  Assim o cliente carrega exatamente os 39 mods (Game 1267 / World 4450),
::  igual ao servidor. Sem isso o cliente roda vanilla e NENHUMA acao
::  sincroniza (porta, agua, comida).
::
::  Coloque este arquivo na raiz do servidor (ao lado do MODS.txt).
:: =====================================================================

title DayZ - Apocalipse (cliente)

set "serverDir=%~dp0"
set "modsFile=MODS.txt"
set "dayzExe=C:\Program Files (x86)\Steam\steamapps\common\DayZ\DayZ_x64.exe"
set "serverIp=127.0.0.1"
set "serverPort=2302"

if not exist "%dayzExe%" (
    echo [ERRO] DayZ_x64.exe nao encontrado:
    echo        %dayzExe%
    echo Edite a variavel dayzExe neste arquivo.
    pause
    exit /b 1
)

if not exist "%modsFile%" (
    echo [ERRO] %modsFile% nao encontrado nesta pasta.
    pause
    exit /b 1
)

set "mods="
set "modCount=0"
set "missing="

for /f "usebackq tokens=* delims=" %%L in ("%modsFile%") do (
    set "line=%%L"
    if defined line if not "!line:~0,1!"=="#" (
        if exist "%serverDir%!line!\addons" (
            if defined mods (
                set "mods=!mods!;%serverDir%!line!"
            ) else (
                set "mods=%serverDir%!line!"
            )
            set /a modCount+=1
        ) else (
            set "missing=!missing! !line!"
        )
    )
)

if defined missing (
    echo [AVISO] mods listados no MODS.txt sem pasta addons:
    echo         !missing!
    echo.
)

if not defined mods (
    echo [ERRO] nenhum mod valido encontrado.
    pause
    exit /b 1
)

echo Mods carregados: !modCount!
echo Conectando em %serverIp%:%serverPort% ...
echo.

start "" "%dayzExe%" "-mod=!mods!" -connect=%serverIp% -port=%serverPort% -skipIntro -nosplash

endlocal
