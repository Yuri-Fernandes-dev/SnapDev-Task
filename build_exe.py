#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil
import sys

def build_executable():
    """
    Script para criar um executável do sistema Kanban usando PyInstaller.
    """
    print("="*80)
    print("Criando executável do SnapDev Task")
    print("="*80)
    
    # Verificar se o PyInstaller está instalado
    try:
        import PyInstaller
        print("PyInstaller encontrado.")
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Verificar o ícone
    icon_path = "img.ico"
    if not os.path.exists(icon_path):
        print(f"AVISO: Ícone {icon_path} não encontrado. O executável será criado sem ícone personalizado.")
        icon_param = ""
    else:
        print(f"Ícone encontrado: {icon_path}")
        icon_param = f"--icon={icon_path}"
    
    # Limpar diretórios de build anteriores
    print("\nLimpando builds anteriores...")
    for dir_to_clean in ["build", "dist"]:
        if os.path.exists(dir_to_clean):
            shutil.rmtree(dir_to_clean)
            print(f"  Diretório {dir_to_clean} removido.")
    
    # Verificar dependências
    print("\nVerificando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Gerar o arquivo de especificação
    print("\nGerando arquivo de especificação...")
    spec_file = "SnapDevTask.spec"
    
    with open(spec_file, "w") as f:
        f.write(f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('alarme.wav', '.'),
        ('EsteLogo.png', '.'),
        ('tasks.db', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SnapDevTask',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['{icon_path}'],
)
""")
    
    # Executar o PyInstaller
    print("\nExecutando PyInstaller para criar o executável...")
    subprocess.run(["pyinstaller", spec_file, "--clean"])
    
    # Verificar se o executável foi criado com sucesso
    exe_path = os.path.join("dist", "SnapDevTask.exe")
    if os.path.exists(exe_path):
        print("\n"+"="*80)
        print(f"Executável criado com sucesso: {exe_path}")
        print("="*80)
        
        # Criar atalho na área de trabalho
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "SnapDev Task.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = os.path.abspath(exe_path)
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(exe_path))
            shortcut.IconLocation = os.path.abspath(icon_path)
            shortcut.save()
            
            print(f"\nAtalho criado na área de trabalho: {shortcut_path}")
        except Exception as e:
            print(f"\nNão foi possível criar o atalho na área de trabalho: {e}")
            print("Você pode criar o atalho manualmente.")
    else:
        print("\n"+"="*80)
        print("ERRO: Não foi possível criar o executável.")
        print("="*80)

if __name__ == "__main__":
    build_executable() 