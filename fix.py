#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corrigir problemas de estilo nas tarefas do Kanban.
Este script modifica diretamente os arquivos de estilo para garantir
que os itens das tarefas nunca fiquem transparentes.
"""

import os

# Caminho do arquivo de estilo
STYLE_FILE = os.path.join("app", "utils", "style.py")

def fix_style_file():
    """Modifica o arquivo de estilo para corrigir o problema de transparência"""
    if not os.path.exists(STYLE_FILE):
        print(f"Erro: Arquivo de estilo não encontrado: {STYLE_FILE}")
        return False
    
    # Ler o conteúdo atual do arquivo
    with open(STYLE_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Adicionar estilo de correção que sobrescreve qualquer estilo existente
    FIX_STYLE = """
# Estilos de correção para o problema de transparência
FIXED_STYLES = '''
    QListWidget::item,
    QListWidget::item:selected,
    QListWidget::item:focus,
    QListWidget::item:hover {
        background-color: white !important;
    }
    
    QListWidget[column="to_do"]::item,
    QListWidget[column="to_do"]::item:selected,
    QListWidget[column="to_do"]::item:focus,
    QListWidget[column="to_do"]::item:hover {
        background-color: white !important;
        border-left: 4px solid #2196f3;
    }
    
    QListWidget[column="doing"]::item,
    QListWidget[column="doing"]::item:selected,
    QListWidget[column="doing"]::item:focus,
    QListWidget[column="doing"]::item:hover {
        background-color: white !important;
        border-left: 4px solid #ffc107;
    }
    
    QListWidget[column="done"]::item,
    QListWidget[column="done"]::item:selected,
    QListWidget[column="done"]::item:focus,
    QListWidget[column="done"]::item:hover {
        background-color: white !important;
        border-left: 4px solid #4caf50;
    }
'''
"""
    
    # Modificar o arquivo KANBAN_STYLE para incluir nosso novo estilo fixo
    if "FIXED_STYLES" not in content:
        # Adicionar o estilo fixo no final do arquivo
        content += FIX_STYLE
        
        # Modificar a definição de KANBAN_STYLE para incluir nosso estilo fixo
        content = content.replace("KANBAN_STYLE = f\"\"\"", "KANBAN_STYLE = f\"\"\"\n    {FIXED_STYLES}")
    
        # Salvar o arquivo modificado
        with open(STYLE_FILE, 'w', encoding='utf-8') as file:
            file.write(content)
        
        print(f"✅ O arquivo de estilo foi modificado com sucesso: {STYLE_FILE}")
        return True
    else:
        print("O arquivo já foi corrigido anteriormente.")
        return False

def main():
    """Função principal"""
    print("🔧 Iniciando correção de estilos do Kanban...")
    fix_style_file()
    print("✨ Concluído! Execute o aplicativo novamente para ver as mudanças.")

if __name__ == "__main__":
    main() 