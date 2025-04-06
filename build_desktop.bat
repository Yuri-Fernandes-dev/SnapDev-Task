@echo off
echo ===================================================
echo Criando executavel desktop do SnapDev Task
echo ===================================================

echo Instalando dependencias necessarias...
pip install pyinstaller pywin32 winshell

echo.
echo Executando script de criacao do executavel...
python build_exe.py

echo.
echo ===================================================
echo Processo concluido!
echo ===================================================
echo.
echo O executavel foi criado na pasta dist/
echo Um atalho foi criado na sua area de trabalho

echo.
echo Pressione qualquer tecla para sair...
pause > nul 