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

if not exist "%dayzExe%" goto :sem_exe
if not exist "%modsFile%" goto :sem_mods

set "mods="
set "modCount=0"
set "missing="

for /f "usebackq tokens=* delims=" %%L in ("%modsFile%") do call :add_mod "%%L"

if defined missing echo [AVISO] mods no MODS.txt sem pasta addons: !missing!
echo.
if not defined mods goto :sem_mods
if %modCount%==0 goto :sem_mods

echo Mods carregados: %modCount%
echo Conectando em %serverIp%:%serverPort% ...
echo.

start "" "%dayzExe%" "-mod=!mods!" -connect=%serverIp% -port=%serverPort% -skipIntro -nosplash
endlocal
exit /b 0

:add_mod
set "line=%~1"
if not defined line exit /b 0
if "!line:~0,1!"=="#" exit /b 0
if not exist "%serverDir%!line!\addons" goto :add_mod_missing
if defined mods goto :add_mod_append
set "mods=%serverDir%!line!"
set /a modCount+=1
exit /b 0
:add_mod_append
set "mods=!mods!;%serverDir%!line!"
set /a modCount+=1
exit /b 0
:add_mod_missing
set "missing=!missing! !line!"
exit /b 0

:sem_exe
echo [ERRO] DayZ_x64.exe nao encontrado em:
echo.
echo    "%dayzExe%"
echo.
echo Edite a variavel dayzExe neste arquivo.
pause
exit /b 1

:sem_mods
echo [ERRO] Nenhum mod valido encontrado.
echo Verifique se este arquivo esta na raiz do servidor, ao lado do MODS.txt,
echo e se as pastas @Mod possuem subpasta addons.
pause
exit /b 1
