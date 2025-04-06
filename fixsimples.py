#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corrigir o problema de transparência nas tarefas do Kanban,
modificando diretamente o CSS no arquivo kanban_board.py.
"""

import os
import re

# Caminho para o arquivo kanban_board.py
KANBAN_BOARD_FILE = os.path.join("app", "components", "kanban_board.py")

def fix_kanban_board():
    """Modifica o estilo das tarefas diretamente no arquivo kanban_board.py"""
    
    if not os.path.exists(KANBAN_BOARD_FILE):
        print(f"Erro: Arquivo kanban_board.py não encontrado: {KANBAN_BOARD_FILE}")
        return False
    
    # Ler o conteúdo do arquivo
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Expressão regular para encontrar a definição do estilo da lista
    pattern = r'list_style = f""".*?"""'
    
    # Novo estilo com correção de transparência
    new_style = r'''list_style = f"""
            QListWidget {{ 
                background-color: {("#bbdefb" if column_id == "to_do" else "#fff9c4" if column_id == "doing" else "#c8e6c9")};
                border: 1px solid {border_color};
                border-radius: 5px;
            }}
            
            QListWidget::item {{
                background-color: white !important;
                border-left: 5px solid {border_color};
                border-top: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 5px;
                margin: 5px;
            }}
            
            QListWidget::item:selected {{ 
                background-color: white !important;
                border-left: 5px solid {border_color};
                border-right: 1px solid #bbbbbb;
                border-top: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
            
            QListWidget::item:focus {{ 
                background-color: white !important;
                outline: none;
                border-right: 1px solid #bbbbbb;
                border-top: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
            
            QListWidget::item:hover {{
                background-color: white !important;
                border-right: 1px solid #bbbbbb;
                border-top: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
        """'''
    
    # Substituir apenas a definição do estilo
    modified_content = re.sub(pattern, new_style, content, flags=re.DOTALL)
    
    # Salvar o arquivo modificado
    with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
        file.write(modified_content)
    
    print(f"✅ Arquivo kanban_board.py modificado com sucesso!")
    return True

def main():
    """Função principal"""
    print("🔧 Iniciando correção simples de estilos do Kanban...")
    fix_kanban_board()
    print("✨ Concluído! Execute o aplicativo novamente para ver as mudanças.")

if __name__ == "__main__":
    main() 