#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Este script substitui completamente o estilo das tarefas no arquivo kanban_board.py.
É uma solução simples e garantida para o problema de transparência.
"""

import os
import re

# Caminho para o arquivo
KANBAN_BOARD_FILE = os.path.join("app", "components", "kanban_board.py")

def fix():
    """Substitui completamente o estilo das tarefas"""
    if not os.path.exists(KANBAN_BOARD_FILE):
        print(f"Erro: Arquivo não encontrado: {KANBAN_BOARD_FILE}")
        return False
    
    # Ler o conteúdo do arquivo
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Novo código para substituir o estilo
    style_code = '''
            # Criar o CSS para a lista e para os itens com borda esquerda colorida
            list_style = f"""
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
                    border-top: 1px solid #bbbbbb !important;
                    border-right: 1px solid #bbbbbb !important;
                    border-bottom: 1px solid #bbbbbb !important;
                }}
                
                QListWidget::item:focus {{ 
                    background-color: white !important;
                    outline: none;
                    border-left: 5px solid {border_color};
                    border-top: 1px solid #bbbbbb !important;
                    border-right: 1px solid #bbbbbb !important;
                    border-bottom: 1px solid #bbbbbb !important;
                }}
                
                QListWidget::item:hover {{
                    background-color: white !important;
                    border-left: 5px solid {border_color};
                    border-top: 1px solid #bbbbbb !important;
                    border-right: 1px solid #bbbbbb !important;
                    border-bottom: 1px solid #bbbbbb !important;
                }}
            """'''
    
    # Padrão para encontrar a definição do estilo
    pattern = r"# Criar o CSS para a lista e para os itens com borda esquerda colorida.*?list_style = f\"\"\".*?\"\"\""
    
    # Substituir o estilo
    modified_content = re.sub(pattern, style_code, content, flags=re.DOTALL)
    
    # Também modificar o comportamento do dropEvent na classe CustomListWidget
    drop_event_pattern = r"def dropEvent\(self, event\):.*?self\.update_all_items\(\)"
    
    drop_event_code = '''    def dropEvent(self, event):
        # Executa o comportamento padrão
        super().dropEvent(event)
        
        # Força atualização visual de todos os itens após soltar
        for i in range(self.count()):
            item = self.item(i)
            if item:
                item.setBackground(QColor("#FFFFFF"))
        
        # Notificar outras colunas para atualizar também
        if self.parent() and hasattr(self.parent(), "parent") and self.parent().parent():
            board = self.parent().parent()
            if hasattr(board, "columns"):
                for column_id, column in board.columns.items():
                    column.update_all_items_appearance()'''
    
    # Substituir o método dropEvent
    modified_content = re.sub(drop_event_pattern, drop_event_code, modified_content, flags=re.DOTALL)
    
    # Salvar o arquivo modificado
    with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
        file.write(modified_content)
    
    print("✅ Correção aplicada com sucesso!")
    print("Agora execute o aplicativo para ver as mudanças.")
    
    return True

if __name__ == "__main__":
    print("🔧 Aplicando correção final para o problema de transparência nas tarefas...")
    fix() 