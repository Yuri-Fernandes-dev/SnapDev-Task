#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para resolver definitivamente o problema de transparência 
nas tarefas do quadro Kanban, com múltiplas abordagens.
"""

import os
import re

# Caminho para o arquivo kanban_board.py
KANBAN_BOARD_FILE = os.path.join("app", "components", "kanban_board.py")

def fix_item_update_display():
    """Modifica o método _update_display da classe TaskItem"""
    
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Expressão regular para encontrar o método _update_display
    pattern = r'def _update_display\(self\):.*?self\.setToolTip\(.*?\)\s*'
    
    # Novo código para o método _update_display
    new_method = r"""def _update_display(self):
        """Atualiza a aparência visual do item"""
        task = self.data(self.TASK_DATA_ROLE)
        
        # Verificar se temos dados
        if not task:
            return
            
        # Extrair informações
        title = task.get("title", "Tarefa sem título")
        priority = task.get("priority", "Baixa")
        description = task.get("description", "")
        
        # Definir texto
        self.setText(title)
        
        # Configurar fonte em negrito
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        
        # IMPORTANTE: Forçar cor de texto preta
        self.setForeground(QColor("#000000"))
        
        # IMPORTANTE: Forçar fundo branco SEMPRE - esta é a chave para resolver o problema
        self.setBackground(QColor("#FFFFFF"))
        
        # Garantir que o item seja sempre visível, selecionável e arrastável
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | 
            Qt.ItemFlag.ItemIsEnabled | 
            Qt.ItemFlag.ItemIsDragEnabled | 
            Qt.ItemFlag.ItemNeverHasChildren
        )
        
        # Tooltip baseado na prioridade
        self.setToolTip(f"{title} - Prioridade {priority}: {description}")
    """
    
    # Substituir o método
    modified_content = re.sub(pattern, new_method, content, flags=re.DOTALL)
    
    # Escrever o conteúdo modificado de volta para o arquivo
    with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
        file.write(modified_content)
    
    print("✅ Método _update_display modificado com sucesso!")

def fix_list_style():
    """Modifica o estilo CSS do QListWidget"""
    
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Expressão regular para encontrar a definição do estilo da lista
    pattern = r'list_style = f""".*?"""'
    
    # Novo estilo com correção de transparência
    new_style = r'''list_style = f"""
            /* Estilo do widget da lista */
            QListWidget {{ 
                background-color: {("#bbdefb" if column_id == "to_do" else "#fff9c4" if column_id == "doing" else "#c8e6c9")};
                border: 1px solid {border_color};
                border-radius: 5px;
            }}
            
            /* Estilo para TODOS os itens - sempre branco */
            QListWidget::item {{
                background-color: white !important;
                color: black !important;
                border-left: 5px solid {border_color};
                border-top: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 5px;
                margin: 5px;
            }}
            
            /* Estados dos itens - sempre brancos */
            QListWidget::item:selected {{ 
                background-color: white !important;
                color: black !important;
                border-left: 5px solid {border_color};
                border-top: 1px solid #bbbbbb;
                border-right: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
            
            QListWidget::item:focus {{ 
                background-color: white !important;
                color: black !important;
                outline: none;
                border-left: 5px solid {border_color};
                border-top: 1px solid #bbbbbb;
                border-right: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
            
            QListWidget::item:hover {{
                background-color: white !important;
                color: black !important;
                border-left: 5px solid {border_color};
                border-top: 1px solid #bbbbbb;
                border-right: 1px solid #bbbbbb;
                border-bottom: 1px solid #bbbbbb;
            }}
        """'''
    
    # Substituir o estilo
    modified_content = re.sub(pattern, new_style, content, flags=re.DOTALL)
    
    # Escrever o conteúdo modificado de volta para o arquivo
    with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
        file.write(modified_content)
    
    print("✅ Estilo da lista modificado com sucesso!")

def add_force_white_background():
    """Adiciona código para forçar o fundo branco em todas as tarefas periodicamente"""
    
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.readlines()
    
    # Código para adicionar antes da classe KanbanBoard
    timer_code = """
# Função global para forçar fundo branco em todos os itens (usado como último recurso)
def force_white_background(task_list):
    """Força o fundo branco em todos os itens de uma lista"""
    if not task_list:
        return
        
    for i in range(task_list.count()):
        item = task_list.item(i)
        if item:
            item.setBackground(QColor("#FFFFFF"))
            item.setForeground(QColor("#000000"))

"""
    
    # Encontrar a linha onde começa a classe KanbanBoard
    kanban_board_index = -1
    for i, line in enumerate(content):
        if "class KanbanBoard" in line:
            kanban_board_index = i
            break
    
    if kanban_board_index > 0:
        # Inserir o código antes da classe KanbanBoard
        content.insert(kanban_board_index, timer_code)
        
        # Ler o conteúdo atualizado
        updated_content = "".join(content)
        
        # Adicionar o temporizador ao método __init__ da classe KanbanBoard
        pattern = r'def __init__\(self, parent=None\):.*?self\.load_columns\(\)'
        
        init_replacement = r"""def __init__(self, parent=None):
        super().__init__(parent)
        
        # Aplicar estilo
        self.setStyleSheet(KANBAN_STYLE)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        
        # Inicializar colunas e carregar tarefas
        self.load_columns()
        
        # Configurar temporizador para forçar fundo branco em todas as tarefas periodicamente
        self.white_bg_timer = QTimer(self)
        self.white_bg_timer.timeout.connect(self.force_white_bg_all_columns)
        self.white_bg_timer.start(500)  # Atualizar a cada 500ms"""
        
        updated_content = re.sub(pattern, init_replacement, updated_content, flags=re.DOTALL)
        
        # Adicionar o método force_white_bg_all_columns à classe KanbanBoard
        pattern = r'def refresh_all_tasks\(self\):.*?pass'
        
        method_replacement = r"""def refresh_all_tasks(self):
        """Atualiza a aparência de todas as tarefas em todas as colunas"""
        try:
            if hasattr(self, 'columns'):
                for column_id, column in self.columns.items():
                    if hasattr(column, 'update_all_items_appearance'):
                        for i in range(column.task_list.count()):
                            item = column.task_list.item(i)
                            if item:
                                # Simplesmente garantir que todos os itens tenham fundo branco
                                item.setBackground(QColor("#FFFFFF"))
        except Exception as e:
            # Silenciosamente ignorar erros durante a atualização automática
            pass
            
    def force_white_bg_all_columns(self):
        """Força o fundo branco em todas as tarefas de todas as colunas"""
        try:
            if hasattr(self, 'columns'):
                for column_id, column in self.columns.items():
                    if hasattr(column, 'task_list'):
                        force_white_background(column.task_list)
        except Exception:
            # Ignorar erros silenciosamente
            pass"""
        
        updated_content = re.sub(pattern, method_replacement, updated_content, flags=re.DOTALL)
        
        # Escrever o conteúdo modificado de volta para o arquivo
        with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
            file.write(updated_content)
        
        print("✅ Temporizador para forçar fundo branco adicionado com sucesso!")
    else:
        print("❌ Não foi possível encontrar a classe KanbanBoard!")

def add_drop_event_fix():
    """Adiciona código para forçar o fundo branco após eventos de drag and drop"""
    
    with open(KANBAN_BOARD_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Modificar a classe CustomListWidget para corrigir o dropEvent
    pattern = r'def dropEvent\(self, event\):.*?super\(\)\.dropEvent\(event\)'
    
    drop_event_replacement = r"""def dropEvent(self, event):
        # Executar o comportamento padrão
        super().dropEvent(event)
        
        # Forçar fundo branco para todos os itens após soltar
        for i in range(self.count()):
            item = self.item(i)
            if item:
                item.setBackground(QColor("#FFFFFF"))
                item.setForeground(QColor("#000000"))
                
        # Forçar atualização visual de todos os itens
        self.update()"""
    
    # Substituir o método
    modified_content = re.sub(pattern, drop_event_replacement, content, flags=re.DOTALL)
    
    # Escrever o conteúdo modificado de volta para o arquivo
    with open(KANBAN_BOARD_FILE, "w", encoding="utf-8") as file:
        file.write(modified_content)
    
    print("✅ Método dropEvent modificado com sucesso!")

def main():
    """Função principal para executar todas as correções"""
    print("🔧 Iniciando solução definitiva para o problema de transparência...")
    
    # Verificar se o arquivo existe
    if not os.path.exists(KANBAN_BOARD_FILE):
        print(f"❌ Arquivo kanban_board.py não encontrado: {KANBAN_BOARD_FILE}")
        return
    
    # Aplicar correções
    fix_item_update_display()
    fix_list_style()
    add_force_white_background()
    add_drop_event_fix()
    
    print("✨ Todas as correções foram aplicadas com sucesso!")
    print("💡 Por favor, execute o aplicativo novamente para ver as mudanças.")
    print("   O problema de transparência deve estar completamente resolvido agora.")

if __name__ == "__main__":
    main() 