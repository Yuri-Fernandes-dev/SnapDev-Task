#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import time
import sys
import sqlite3

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit,
    QFormLayout, QTextEdit, QComboBox, QMessageBox, QMenu, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QDateTime, QSize, QPoint
from PySide6.QtGui import QColor, QFont, QIcon

from app.utils.style import (
    KANBAN_STYLE, DIALOG_STYLE, 
    HIGH_PRIORITY_COLOR, MEDIUM_PRIORITY_COLOR, LOW_PRIORITY_COLOR,
    TODO_COLOR, IN_PROGRESS_COLOR, DONE_COLOR,
    PRIMARY_COLOR
)

# Configurações
DB_FILE = "tasks.db"

# Colunas do Kanban
COLUMNS = {
    "to_do": {"name": "A Fazer", "color": "#2196f3"},
    "doing": {"name": "Em Andamento", "color": "#ffc107"},
    "done": {"name": "Concluído", "color": "#4caf50"}
}

# Classe personalizada para QListWidget que força atualização visual após drag and drop
class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
    
    def dropEvent(self, event):
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
                    column.update_all_items_appearance()
    
    def update_all_items(self):
        """Atualiza todos os itens na lista"""
        for i in range(self.count()):
            item = self.item(i)
            if item:
                if isinstance(item, TaskItem):
                    item.update_display()
                # Forçar fundo branco para todos os itens
                item.setBackground(QColor("#FFFFFF"))
    
    def update(self):
        """Sobrescreve o método update para compatibilidade com chamadas sem argumentos"""
        # Chamar o método repaint para atualizar a renderização
        self.repaint()

# Estilos para itens de tarefa baseados na coluna
TASK_ITEM_STYLES = {
    "to_do": "background-color: white; border-left: 5px solid #2196f3; border-top: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; border-radius: 3px; padding: 8px; min-height: 60px;",
    "doing": "background-color: white; border-left: 5px solid #ffc107; border-top: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; border-radius: 3px; padding: 8px; min-height: 60px;",
    "done": "background-color: white; border-left: 5px solid #4caf50; border-top: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; border-radius: 3px; padding: 8px; min-height: 60px;"
}

# Função para inicializar o banco de dados
def init_db():
    # Criar ou conectar ao banco de dados
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Criar tabela de tarefas se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT,
        column_id TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Inicializar banco de dados
init_db()


class TaskDialog(QDialog):
    """Diálogo para adicionar ou editar tarefas"""
    
    def __init__(self, parent=None, task=None, view_only=False):
        super().__init__(parent)
        self.task = task or {}
        self.view_only = view_only
        
        # Definir título baseado no modo
        if view_only:
            self.setWindowTitle("Visualizar Tarefa")
        else:
            self.setWindowTitle("Nova Tarefa" if not task else "Editar Tarefa")
        
        # Aumentar largura e altura para evitar cortes
        self.setMinimumWidth(550)
        self.setMinimumHeight(480)
        
        # Centralizar na tela
        if parent:
            parent_center = parent.mapToGlobal(parent.rect().center())
            dialog_width = self.width()
            dialog_height = self.height()
            self.setGeometry(parent_center.x() - dialog_width // 2, 
                             parent_center.y() - dialog_height // 2,
                             dialog_width, dialog_height)
        
        # Remover barra de título da janela (para personalização)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Criar efeito de sombra
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Aplicar estilo
        self.setStyleSheet(DIALOG_STYLE)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container principal com sombra
        main_container = QWidget()
        main_container.setObjectName("main_container")
        main_container.setStyleSheet("""
            QWidget#main_container {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Criar cabeçalho personalizado
        header = QWidget()
        header.setObjectName("modal_header")
        header.setStyleSheet(f"""
            QWidget#modal_header {{
                background-color: {PRIMARY_COLOR};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                min-height: 60px;
            }}
            QLabel#header_title {{
                color: white;
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton#close_header_button {{
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton#close_header_button:hover {{
                color: rgba(255, 255, 255, 0.8);
            }}
            QPushButton#close_header_button:pressed {{
                color: rgba(255, 255, 255, 0.6);
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Título no cabeçalho
        title_text = ""
        if view_only:
            title_text = "Visualizar Tarefa"
        else:
            title_text = "Nova Tarefa" if not task else "Editar Tarefa"
            
        header_title = QLabel(title_text)
        header_title.setObjectName("header_title")
        header_layout.addWidget(header_title)
        
        # Botão de fechar no cabeçalho
        close_button = QPushButton("✕")
        close_button.setObjectName("close_header_button")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(close_button)
        
        # Adicionar cabeçalho ao layout principal
        main_layout.addWidget(header)
        
        # Container para o conteúdo
        content_container = QWidget()
        content_container.setObjectName("content_container")
        content_container.setStyleSheet("""
            QWidget#content_container {
                background-color: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Campos
        title_label = QLabel("Título:")
        title_label.setObjectName("field_label")
        
        self.title_input = QLineEdit(self.task.get("title", ""))
        self.title_input.setMinimumHeight(50)  # Aumentar altura
        self.title_input.setFont(QFont("Arial", 11))  # Definir fonte maior
        self.title_input.setPlaceholderText("Digite o título da tarefa")
        self.title_input.returnPressed.connect(self.accept)  # Conectar a tecla Enter para salvar
        self.title_input.setFocus()  # Colocar foco no campo de título
        
        desc_label = QLabel("Descrição:")
        desc_label.setObjectName("field_label")
        
        self.description_input = QTextEdit(self.task.get("description", ""))
        self.description_input.setMinimumHeight(150)  # Aumentar altura
        self.description_input.setFont(QFont("Arial", 11))  # Definir fonte maior
        self.description_input.setPlaceholderText("Descreva a tarefa em detalhes...")
        
        prio_label = QLabel("Prioridade:")
        prio_label.setObjectName("field_label")
        
        self.priority_combo = QComboBox()
        self.priority_combo.setMinimumHeight(50)  # Aumentar altura
        self.priority_combo.setFont(QFont("Arial", 11))  # Definir fonte maior
        self.priority_combo.addItem("Baixa")
        self.priority_combo.addItem("Média")
        self.priority_combo.addItem("Alta")
        
        if "priority" in self.task:
            index = self.priority_combo.findText(self.task["priority"])
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        
        # Se for apenas visualização, desabilitar edição
        if view_only:
            self.title_input.setReadOnly(True)
            self.description_input.setReadOnly(True)
            self.priority_combo.setEnabled(False)
        
        # Adicionar campos ao formulário
        form_layout.addRow(title_label, self.title_input)
        form_layout.addRow(desc_label, self.description_input)
        form_layout.addRow(prio_label, self.priority_combo)
        
        # Adicionar formulário ao layout de conteúdo
        content_layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        if view_only:
            # No modo de visualização, mostrar botões Editar e Fechar
            edit_button = QPushButton("Editar")
            edit_button.setMinimumHeight(50)
            edit_button.setMinimumWidth(130)
            edit_button.setFont(QFont("Arial", 11))
            edit_button.clicked.connect(self.switch_to_edit_mode)
            button_layout.addWidget(edit_button)
            
            button_layout.addStretch()
            
            close_button = QPushButton("Fechar")
            close_button.setMinimumHeight(50)
            close_button.setMinimumWidth(130)
            close_button.setFont(QFont("Arial", 11))
            close_button.clicked.connect(self.reject)
            button_layout.addWidget(close_button)
        else:
            # No modo de edição, mostrar botões Cancelar e Salvar
            button_layout.addStretch()
            
            cancel_button = QPushButton("Cancelar")
            cancel_button.setMinimumHeight(50)
            cancel_button.setMinimumWidth(130)
            cancel_button.setFont(QFont("Arial", 11))
            cancel_button.clicked.connect(self.reject)
            
            save_button = QPushButton("Salvar")
            save_button.setMinimumHeight(50)
            save_button.setMinimumWidth(130)
            save_button.setFont(QFont("Arial", 11))
            save_button.clicked.connect(self.accept)
            
            button_layout.addWidget(cancel_button)
            button_layout.addWidget(save_button)
        
        # Adicionar botões ao layout de conteúdo
        content_layout.addLayout(button_layout)
        
        # Adicionar container de conteúdo ao layout principal
        main_layout.addWidget(content_container)
        
        # Adicionar o container principal ao layout
        layout.addWidget(main_container)
    
    def switch_to_edit_mode(self):
        """Alterna do modo de visualização para o modo de edição"""
        # Rejeitar o diálogo atual
        self.reject()
        
        # Criar um novo diálogo no modo de edição
        edit_dialog = TaskDialog(self.parent(), self.task, view_only=False)
        edit_dialog.exec()
        
        # Atualizar a tarefa se a edição foi aceita
        if edit_dialog.result() == QDialog.Accepted:
            self.parent().edit_task_result(edit_dialog.get_task_data())
    
    def get_task_data(self):
        """Retorna os dados da tarefa do formulário"""
        try:
            # Obter os dados dos campos de entrada
            title = self.title_input.text().strip()
            description = self.description_input.toPlainText().strip()
            priority = self.priority_combo.currentText()
            
            # Se title estiver vazio, definir um valor padrão
            if not title:
                title = "Tarefa sem título"
            
            # Criar um dicionário com os dados da tarefa
            task_data = {
                "title": title,
                "description": description,
                "priority": priority
            }
            
            # Se for uma tarefa existente, preservar o ID e a coluna
            if hasattr(self, 'task') and isinstance(self.task, dict):
                if "id" in self.task:
                    task_data["id"] = self.task["id"]
                if "column" in self.task:
                    task_data["column"] = self.task["column"]
            
            return task_data
        except Exception as e:
            print(f"Erro ao obter dados da tarefa: {e}")
            return {"title": "Tarefa sem título", "description": "", "priority": "Baixa"}
        
    # Permitir mover a janela quando clicar e arrastar no cabeçalho
    def mousePressEvent(self, event):
        if event.position().y() <= 60:  # Se o clique for no cabeçalho
            self.oldPos = event.globalPosition().toPoint()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def showEvent(self, event):
        """Chamado quando o diálogo é mostrado na tela"""
        super().showEvent(event)
        
        # Centralizar diálogo na tela quando for exibido
        if self.parent():
            # Recalcular o tamanho do diálogo após ele ser totalmente construído
            parent_geometry = self.parent().geometry()
            dialog_size = self.size()
            
            # Calcular posição central
            x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
            
            # Mover para o centro
            self.move(x, y)


class TaskItem(QListWidgetItem):
    """Item de tarefa personalizado para o Kanban"""
    
    TASK_DATA_ROLE = Qt.ItemDataRole.UserRole + 1
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        
        # Criar uma cópia simples do dicionário com apenas os dados essenciais
        safe_data = {}
        
        # Copiar apenas campos conhecidos e valores primitivos
        for field in ["title", "description", "priority", "column", "id"]:
            if field in task_data:
                safe_data[field] = task_data[field]
        
        # Garantir que todos os campos obrigatórios existam
        if "title" not in safe_data:
            safe_data["title"] = "Tarefa sem título"
        if "description" not in safe_data:
            safe_data["description"] = ""
        if "priority" not in safe_data:
            safe_data["priority"] = "Baixa"
            
        # Armazenar a cópia dos dados
        self.setData(self.TASK_DATA_ROLE, safe_data)
        
        # Definir altura mínima para a tarefa
        self.setSizeHint(QSize(0, 80))
        
        # Atualizar a aparência
        self._update_display()
        
        # Garantir que o item seja sempre visível com fundo branco
        self.ensure_visible()
    
    def ensure_visible(self):
        """Garante que o item seja sempre visível com fundo branco"""
        # Aplicar cores explicitamente
        self.setBackground(QColor("#FFFFFF"))
        self.setForeground(QColor("#000000"))
        
        # Definir tamanho mínimo para garantir altura adequada
        current_size = self.sizeHint()
        if current_size.height() < 80:
            self.setSizeHint(QSize(current_size.width(), 80))
        
        # Definir flags específicas para garantir visibilidade
        self.setFlags(Qt.ItemFlag.ItemIsSelectable | 
                     Qt.ItemFlag.ItemIsEnabled | 
                     Qt.ItemFlag.ItemIsDragEnabled | 
                     Qt.ItemFlag.ItemNeverHasChildren)
    
    def _update_display(self):
        """Atualiza a aparência visual do item"""
        try:
            # Obter os dados da tarefa
            task = self.data(self.TASK_DATA_ROLE)
            
            # Verificar se temos dados
            if not task:
                return
            
            # Extrair informações
            title = task.get("title", "Tarefa sem título")
            priority = task.get("priority", "Baixa")
            
            # Configurar texto e tooltip
            priority_indicator = ""
            tooltip_text = title
            
            if priority == "Alta":
                priority_indicator = " ●"
                tooltip_text += " - Prioridade Alta"
            elif priority == "Média":
                priority_indicator = " ○"
                tooltip_text += " - Prioridade Média"
            
            # Adicionar descrição ao tooltip
            description = task.get('description', '').strip()
            if description:
                tooltip_text += f"\n\n{description}"
            
            # Definir texto e aparência
            self.setText(title + priority_indicator)
            self.setBackground(QColor("#FFFFFF"))
            self.setForeground(QColor("#333333"))
            
            # Definir fonte em negrito
            font = self.font()
            font.setBold(True)
            self.setFont(font)
            
            # Definir tooltip
            self.setToolTip(tooltip_text)
        except Exception as e:
            print(f"Erro ao atualizar exibição: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_display(self):
        """Método público para atualizar a exibição"""
        self._update_display()
        self.ensure_visible()


class KanbanColumn(QWidget):
    """Uma coluna do quadro Kanban"""
    
    task_moved = Signal(dict, str)  # tarefa, nova_coluna
    
    def __init__(self, column_id, title, parent=None):
        super().__init__(parent)
        self.column_id = column_id
        self.title = title
        
        # Aplicar estilo da coluna baseado na cor correspondente
        self.setStyleSheet(f"""
            QWidget {{ 
                background-color: transparent;
            }}
        """)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Cabeçalho
        header_widget = QWidget()
        header_widget.setFixedHeight(50)  # Altura fixa para o cabeçalho
        header_widget.setStyleSheet("background-color: transparent; border: none;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título à esquerda com texto preto simples
        header_label = QLabel(title)
        header_label.setProperty("column_header", column_id)
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: black; background-color: transparent; border: none;")
        header_layout.addWidget(header_label)
        
        # Espaçador para empurrar o botão para a direita
        header_layout.addStretch()
        
        # Botão de adicionar tarefa (apenas na primeira coluna)
        if column_id == "to_do":
            add_button = QPushButton("Adicionar")
            add_button.setObjectName("add_task_button")  # Definir ID para aplicar estilo CSS
            add_button.setFixedSize(120, 35)  # Aumentar tamanho para evitar corte
            add_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            add_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-radius: 4px;
                    font-weight: bold;
                    padding: 2px 10px;
                }}
                QPushButton:hover {{
                    background-color: #64b5f6;
                }}
                QPushButton:pressed {{
                    background-color: #0d47a1;
                }}
            """)
            add_button.clicked.connect(self.add_task)
            header_layout.addWidget(add_button)
        
        # Adicionar o cabeçalho ao layout principal
        layout.addWidget(header_widget)
        
        # Lista de tarefas
        self.task_list = CustomListWidget(self)
        self.task_list.setProperty("column", column_id)
        self.task_list.setDragEnabled(True)
        self.task_list.setAcceptDrops(True)
        self.task_list.setDropIndicatorShown(True)
        self.task_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.task_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.task_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.task_list.setSpacing(8)
        self.task_list.setWordWrap(True)
        
        # Definir estilo da lista baseado na coluna e evitar cor de seleção feia
        list_style = f"""
            QListWidget {{ 
                background-color: {("#bbdefb" if column_id == "to_do" else "#fff9c4" if column_id == "doing" else "#c8e6c9")};
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            
            QListWidget::item {{
                background-color: white !important;
                border: 1px solid #e0e0e0;
                border-left: 5px solid {("#2196f3" if column_id == "to_do" else "#ffc107" if column_id == "doing" else "#4caf50")};
                border-radius: 4px;
                padding: 8px;
                margin: 5px;
                min-height: 80px;
                color: #333333;
            }}
            
            QListWidget::item:selected {{ 
                background-color: white !important;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if column_id == "to_do" else "#ffc107" if column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
            
            QListWidget::item:focus {{ 
                background-color: white !important;
                outline: none;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if column_id == "to_do" else "#ffc107" if column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
            
            QListWidget::item:hover {{
                background-color: white !important;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if column_id == "to_do" else "#ffc107" if column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
        """
        
        self.task_list.setStyleSheet(list_style)
        
        # Conectar eventos
        self.task_list.model().rowsInserted.connect(self.on_rows_inserted)
        
        # Definir largura mínima
        self.setMinimumWidth(300)
        
        layout.addWidget(self.task_list)
    
    def add_task(self):
        # Delegar para o método add_task do KanbanBoard
        if self.parent() and hasattr(self.parent(), "add_task"):
            self.parent().add_task()
    
    def save_task_to_db(self, task_data):
        """Salva uma tarefa no banco de dados"""
        try:
            # Debug info
            print(f"Salvando tarefa no banco: id={task_data.get('id')}, coluna={task_data.get('column')}")
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Verificar se a tarefa já existe
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_data["id"],))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Atualizar tarefa existente
                cursor.execute(
                    "UPDATE tasks SET title = ?, description = ?, priority = ?, column_id = ? WHERE id = ?",
                    (
                        task_data["title"],
                        task_data["description"],
                        task_data["priority"],
                        task_data["column"],
                        task_data["id"]
                    )
                )
                print(f"Tarefa atualizada no banco - ID: {task_data['id']}")
            else:
                # Inserir nova tarefa
                cursor.execute(
                    "INSERT INTO tasks (id, title, description, priority, column_id) VALUES (?, ?, ?, ?, ?)",
                    (
                        task_data["id"],
                        task_data["title"],
                        task_data["description"],
                        task_data["priority"],
                        task_data["column"]
                    )
                )
                print(f"Nova tarefa {task_data['id']} criada na coluna {task_data['column']}")
            
            conn.commit()
            
            # Verificar se a operação foi bem-sucedida
            verify_cursor = conn.cursor()
            verify_cursor.execute("SELECT column_id FROM tasks WHERE id = ?", (task_data["id"],))
            result = verify_cursor.fetchone()
            if result:
                print(f"Verificação: tarefa {task_data['id']} está agora na coluna {result[0]}")
            else:
                print(f"ERRO: Tarefa não encontrada após salvar")
            
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao salvar tarefa no banco: {str(e)}")
            return False
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto para uma tarefa"""
        item = self.task_list.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu(self)
        # Aplicar estilo ao menu
        context_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                background-color: transparent;
                color: #333333;
                padding: 6px 25px;
                min-width: 150px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
                color: #333333;
            }
        """)
        
        # Ações do menu
        edit_action = context_menu.addAction("Editar")
        
        # Menu de movimentação
        move_menu = context_menu.addMenu("Mover para")
        move_menu.setStyleSheet(context_menu.styleSheet())  # Aplicar o mesmo estilo ao submenu
        
        for col_id, col_info in COLUMNS.items():
            if col_id != self.column_id:
                move_menu.addAction(col_info["name"])
        
        delete_action = context_menu.addAction("Excluir")
        
        # Executar menu
        action = context_menu.exec_(self.task_list.mapToGlobal(position))
        
        if not action:
            return
        
        # Processar ação selecionada
        if action == edit_action:
            self.edit_task(item)
        elif action == delete_action:
            self.delete_task(item)
        else:
            # Verificar se é uma ação de movimentação
            for col_id, col_info in COLUMNS.items():
                if action.text() == col_info["name"]:
                    self.move_task(item, col_id)
                    break
    
    def edit_task(self, task_item):
        """Edita uma tarefa existente"""
        # Obter dados atuais
        current_task = task_item.data(TaskItem.TASK_DATA_ROLE)
        
        # Criar diálogo de edição
        dialog = TaskDialog(self, current_task)
        
        if dialog.exec():
            # Obter novos dados
            new_data = dialog.get_task_data()
            
            # Preservar dados importantes
            new_data["id"] = current_task.get("id", "")
            new_data["column"] = current_task.get("column", self.column_id)
            
            # Atualizar o item
            task_item.setData(TaskItem.TASK_DATA_ROLE, new_data)
            task_item.update_display()
            
            # Salvar no banco de dados
            self.save_task_to_db(new_data)
    
    def delete_task(self, task_item):
        """Exclui uma tarefa"""
        confirm = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Tem certeza que deseja excluir a tarefa '{task_item.data(TaskItem.TASK_DATA_ROLE)['title']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            task_data = task_item.data(TaskItem.TASK_DATA_ROLE)
            task_id = task_data.get("id")
            
            # Remover do banco de dados
            if task_id:
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"Erro ao excluir tarefa do banco: {str(e)}")
            
            # Remover da lista
            row = self.task_list.row(task_item)
            self.task_list.takeItem(row)
            
            # Atualizar a aparência das tarefas restantes
            self.update_all_items_appearance()
    
    def move_task(self, task_item, new_column):
        """Move uma tarefa para outra coluna"""
        # Obter dados da tarefa
        task_data = task_item.data(TaskItem.TASK_DATA_ROLE)
        
        # Atualizar coluna
        task_data["column"] = new_column
        
        # Salvar no banco de dados
        self.save_task_to_db(task_data)
        
        # Remover da lista atual
        row = self.task_list.row(task_item)
        self.task_list.takeItem(row)
        
        # Forçar atualização das tarefas restantes
        self.update_all_items_appearance()
        
        # Emitir sinal para adicionar na nova coluna
        self.task_moved.emit(task_data, new_column)
    
    def update_all_items_appearance(self):
        """Atualiza a aparência de todos os itens da lista"""
        # Primeiro aplicar fundo branco a todos os itens
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item:
                # Garantir fundo branco
                item.setBackground(QColor("#FFFFFF"))
                item.setForeground(QColor("#000000"))
                
                # Tentar atualizar usando o método próprio, se disponível
                if isinstance(item, TaskItem):
                    item.update_display()
                    if hasattr(item, 'ensure_visible'):
                        item.ensure_visible()
            
            # Definir altura mínima para todos os itens
            current_size = item.sizeHint()
            if current_size.height() < 70:
                item.setSizeHint(QSize(current_size.width(), 70))
        
        # Forçar atualização visual - usando repaint() em vez de update()
        self.task_list.repaint()
        
        # Aplicar estilo novamente
        # Recriar e replicar o estilo
        list_style = f"""
            QListWidget {{ 
                background-color: {("#bbdefb" if self.column_id == "to_do" else "#fff9c4" if self.column_id == "doing" else "#c8e6c9")};
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            
            QListWidget::item {{
                background-color: white !important;
                border: 1px solid #e0e0e0;
                border-left: 5px solid {("#2196f3" if self.column_id == "to_do" else "#ffc107" if self.column_id == "doing" else "#4caf50")};
                border-radius: 4px;
                padding: 8px;
                margin: 5px;
                min-height: 80px;
                color: #333333;
            }}
            
            QListWidget::item:selected {{ 
                background-color: white !important;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if self.column_id == "to_do" else "#ffc107" if self.column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
            
            QListWidget::item:focus {{ 
                background-color: white !important;
                outline: none;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if self.column_id == "to_do" else "#ffc107" if self.column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
            
            QListWidget::item:hover {{
                background-color: white !important;
                border: 1px solid #bbbbbb;
                border-left: 5px solid {("#2196f3" if self.column_id == "to_do" else "#ffc107" if self.column_id == "doing" else "#4caf50")};
                color: #333333;
            }}
        """
        
        # Aplicar o estilo novamente
        self.task_list.setStyleSheet(list_style)
    
    def get_all_tasks(self):
        """Retorna todas as tarefas da coluna"""
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            if item:
                task_data = item.data(TaskItem.TASK_DATA_ROLE)
                if task_data:
                    # Criar cópia dos dados
                    task_copy = {}
                    for key, value in task_data.items():
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            task_copy[key] = value
                    tasks.append(task_copy)
        return tasks
    
    def on_item_double_clicked(self, item):
        """Manipula o duplo clique em uma tarefa"""
        # Obter dados da tarefa
        task_data = item.data(TaskItem.TASK_DATA_ROLE)
        
        # Abrir diálogo de visualização
        dialog = TaskDialog(self, task_data, view_only=True)
        
        # Salvar referência ao item atual
        self.current_edited_item = item
        
        dialog.exec()
    
    def edit_task_result(self, task_data):
        """Manipula o resultado da edição de tarefa após visualização"""
        if hasattr(self, 'current_edited_item') and self.current_edited_item:
            # Obter dados atuais
            current_data = self.current_edited_item.data(TaskItem.TASK_DATA_ROLE)
            
            # Preservar dados importantes
            task_data["column"] = current_data.get("column", self.column_id)
            task_data["id"] = current_data.get("id", "")
            
            # Atualizar o item
            self.current_edited_item.setData(TaskItem.TASK_DATA_ROLE, task_data)
            self.current_edited_item.update_display()
            
            # Salvar no banco de dados
            self.save_task_to_db(task_data)
    
    def on_rows_inserted(self, parent, first, last):
        """Manipula quando novas linhas são inseridas (tarefas arrastadas)"""
        try:
            # Para debug
            print(f"Linhas inseridas na coluna '{self.column_id}': de {first} até {last}")
            
            # Atualizar coluna de todas as tarefas inseridas
            for row in range(first, last + 1):
                item = self.task_list.item(row)
                if item:
                    task_data = item.data(TaskItem.TASK_DATA_ROLE)
                    if task_data:
                        old_column = task_data.get("column", "")
                        
                        # Verificar se a coluna mudou
                        if old_column != self.column_id:
                            print(f"Atualizando coluna da tarefa {task_data.get('id')} de '{old_column}' para '{self.column_id}'")
                            
                            # Atualizar a coluna no objeto em memória
                            task_data["column"] = self.column_id
                            item.setData(TaskItem.TASK_DATA_ROLE, task_data)
                            
                            # Salvar no banco de dados
                            self.save_task_to_db(task_data)
                            
                            # Notificar a coluna de origem para atualizar suas tarefas
                            if self.parent() and hasattr(self.parent(), 'columns') and old_column in self.parent().columns:
                                old_column_widget = self.parent().columns[old_column]
                                old_column_widget.update_all_items_appearance()
                        else:
                            print(f"Tarefa {task_data.get('id')} já está na coluna '{self.column_id}', nenhuma atualização necessária")
            
            # Garantir que todos os itens nessa coluna estejam corretamente atualizados
            self.update_all_items_appearance()
            
        except Exception as e:
            print(f"Erro ao processar linhas inseridas: {str(e)}")

    def add_task_item(self, task):
        """Adiciona um item de tarefa existente à coluna"""
        try:
            # Criar item simples
            item = TaskItem(task)
            
            # Adicionar à lista
            self.task_list.addItem(item)
            
            # Garantir que o item fique visível
            self.task_list.scrollToItem(item)
            
            return True
        except Exception as e:
            print(f"ERRO ao adicionar item de tarefa: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


class KanbanBoard(QWidget):
    """Quadro Kanban completo"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Definir ID para o quadro
        self.setObjectName("kanban_board")
        
        # Aplicar estilo
        self.setStyleSheet(KANBAN_STYLE)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        
        # Adicionar botão de salvar no topo
        self.add_save_button()
        
        # Inicializar colunas e carregar tarefas
        self.load_columns()
        
        # Configurar um temporizador para garantir que todas as tarefas mantenham a aparência correta
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all_tasks)
        self.refresh_timer.start(2000)  # Atualizar a cada 2 segundos
        
        # Flag para controlar mudanças não salvas
        self.unsaved_changes = False
    
    def add_save_button(self):
        """Adiciona o botão de salvar no topo do kanban"""
        # Criar layout para o botão
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)
        
        # Adicionar espaçador à esquerda para empurrar o botão para a direita
        button_layout.addStretch()
        
        # Criar o botão de salvar
        save_button = QPushButton("Salvar")
        save_button.setObjectName("save_button")  # Definir ID para aplicar estilo CSS
        save_button.clicked.connect(self.save_button_clicked)
        
        # Adicionar o botão ao layout
        button_layout.addWidget(save_button)
        
        # Adicionar o layout ao layout principal
        self.main_layout.addLayout(button_layout)
    
    def save_button_clicked(self):
        """Manipula o clique no botão de salvar"""
        # Mostrar indicador de salvamento
        result = self.save_all_tasks_to_db()
        
        # Mostrar mensagem de confirmação
        if result:
            QMessageBox.information(self, "Salvamento", "Todas as tarefas foram salvas com sucesso!")
        else:
            QMessageBox.warning(self, "Erro ao Salvar", "Ocorreu um erro ao salvar as tarefas. Por favor, tente novamente.")
    
    def handle_task_moved(self, task, new_column):
        """Manipula o evento de tarefa movida entre colunas"""
        try:
            # Log para depuração 
            print(f"Tarefa sendo movida para coluna {new_column}: {task.get('id')}")
            
            # Verificar se a tarefa é válida
            if not isinstance(task, dict) or "id" not in task:
                print(f"Erro: Tarefa inválida recebida para movimentação: {type(task)}")
                return
            
            # Criar uma cópia da tarefa para evitar modificações em cascata
            task_copy = task.copy()
            
            # Garantir que a coluna esteja atualizada no objeto antes de adicionar ao widget
            old_column = task_copy.get("column", "")
            task_copy["column"] = new_column
            
            print(f"Mudança de coluna: Tarefa {task_copy.get('id')} - de '{old_column}' para '{new_column}'")
            
            # Verificar se a coluna de destino existe
            if new_column not in self.columns:
                print(f"Erro: Coluna de destino '{new_column}' não existe")
                return
            
            # Adicionar na nova coluna
            self.columns[new_column].add_task_item(task_copy)
            
            # Sincronizar com o banco de dados
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                # Verificar a coluna atual no banco
                check_cursor = conn.cursor()
                check_cursor.execute("SELECT column_id FROM tasks WHERE id = ?", (task_copy["id"],))
                result = check_cursor.fetchone()
                if result:
                    current_column = result[0]
                    print(f"Coluna atual no banco: {current_column}")
                
                # Atualizar no banco
                cursor.execute(
                    "UPDATE tasks SET column_id = ? WHERE id = ?",
                    (new_column, task_copy["id"])
                )
                
                conn.commit()
                
                # Verificar se a atualização funcionou
                verify_cursor = conn.cursor()
                verify_cursor.execute("SELECT column_id FROM tasks WHERE id = ?", (task_copy["id"],))
                result = verify_cursor.fetchone()
                if result:
                    print(f"Verificação de movimento: tarefa {task_copy['id']} está agora na coluna {result[0]}")
                else:
                    print(f"ERRO: Tarefa não encontrada após mover")
                
                conn.close()
                
                # Atualizar a aparência de todas as tarefas em todas as colunas
                for column_id, column in self.columns.items():
                    column.update_all_items_appearance()
                
            except Exception as e:
                print(f"Erro ao atualizar coluna após mover: {str(e)}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"Erro global ao mover tarefa: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_tasks(self):
        """Carrega tarefas do banco de dados"""
        try:
            # Verificar se o banco de dados existe
            if not os.path.exists(DB_FILE):
                self.initialize_db()
                print(f"Banco de dados criado em {DB_FILE}")
                return []
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Mostrar estrutura da tabela para debug
            try:
                cursor.execute("PRAGMA table_info(tasks)")
                columns = cursor.fetchall()
                print("Estrutura da tabela tasks:")
                for col in columns:
                    print(f"  {col}")
            except Exception as e:
                print(f"Erro ao verificar estrutura da tabela: {str(e)}")
            
            # Buscar todas as tarefas
            cursor.execute("SELECT id, title, description, priority, column_id FROM tasks")
            tasks = []
            
            # Log para debug - mostrar as tarefas carregadas
            print("\nTarefas encontradas no banco de dados:")
            
            for row in cursor.fetchall():
                task_id, title, description, priority, column_id = row
                
                # Verificar se a coluna é válida, caso contrário, corrigir
                if column_id not in ["to_do", "doing", "done"]:
                    print(f"ERRO: Tarefa {task_id} tem coluna inválida: '{column_id}'. Corrigindo para 'to_do'")
                    column_id = "to_do"
                    
                    # Atualizar no banco
                    update_cursor = conn.cursor()
                    update_cursor.execute(
                        "UPDATE tasks SET column_id = ? WHERE id = ?",
                        (column_id, task_id)
                    )
                    conn.commit()
                
                task = {
                    "id": task_id,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "column": column_id  # Usar o column_id diretamente do banco
                }
                
                print(f"  ID: {task_id}, Título: {title}, Coluna: {column_id}")
                tasks.append(task)
            
            conn.close()
            print(f"Total de {len(tasks)} tarefas carregadas do banco\n")
            return tasks
            
        except Exception as e:
            print(f"Erro ao carregar tarefas: {str(e)}")
            # Em caso de erro, inicializar o banco
            self.initialize_db()
            return []
    
    def initialize_db(self):
        # Criar ou conectar ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Criar tabela de tarefas se não existir
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            column_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()

    def load_columns(self):
        """Inicializa as colunas e carrega as tarefas para cada uma"""
        print("\nInicializando colunas do Kanban...")
        
        # Dicionário para armazenar as referências das colunas
        self.columns = {}
        
        # Carregar todas as tarefas do banco de dados primeiro
        tasks = self.load_tasks()
        print(f"Carregadas {len(tasks)} tarefas no total.")
        
        # Criar colunas com os respectivos títulos
        column_layout = QHBoxLayout()
        column_layout.setSpacing(20)
        column_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Criar as três colunas
        titles = {
            "to_do": "A Fazer",
            "doing": "Em Andamento",
            "done": "Concluído"
        }
        
        # Aplicar estilo do Kanban primeiro
        self.setStyleSheet(KANBAN_STYLE)
        
        # Criar cada coluna e adicionar ao layout
        for column_id, title in titles.items():
            print(f"Criando coluna '{column_id}' ({title})")
            column = KanbanColumn(column_id, title, self)
            column.task_moved.connect(self.handle_task_moved)
            column.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.columns[column_id] = column
            column_layout.addWidget(column, 1)
        
        # Agora distribua as tarefas nas colunas corretas
        task_count_by_column = {"to_do": 0, "doing": 0, "done": 0}
        print("\nDistribuindo tarefas para colunas:")
        
        for task in tasks:
            column_id = task.get("column", "to_do")
            
            # Verificar se a coluna existe
            if column_id not in self.columns:
                print(f"Aviso: Coluna '{column_id}' não existe. Movendo tarefa {task['id']} para 'to_do'")
                column_id = "to_do"
                task["column"] = "to_do"
                
                # Atualizar no banco
                try:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE tasks SET column_id = ? WHERE id = ?",
                        (column_id, task["id"])
                    )
                    conn.commit()
                    conn.close()
                    print(f"Banco atualizado: Tarefa {task['id']} movida para coluna 'to_do'")
                except Exception as e:
                    print(f"Erro ao atualizar coluna no banco: {str(e)}")
            
            # Adicionar a tarefa à coluna correta
            print(f"Adicionando tarefa {task['id']} na coluna '{column_id}'")
            self.columns[column_id].add_task_item(task)
            task_count_by_column[column_id] += 1
        
        print(f"\nDistribuição final de tarefas:")
        for col_id, count in task_count_by_column.items():
            print(f"  {titles[col_id]}: {count} tarefas")
        
        # Adicionar o layout de colunas ao layout principal
        self.main_layout.addLayout(column_layout)
        
        # Garantir que o estilo seja aplicado a todos os componentes
        self.refresh_style()
        
        # Aplicar fundo branco manualmente a todos os itens de todas as colunas
        self.apply_white_background_to_all_items()
        
        # Código especial para garantir o fundo branco na primeira tarefa da coluna "done" (verde)
        if "done" in self.columns and self.columns["done"].task_list.count() > 0:
            # Forçar fundo branco para o primeiro item da coluna "concluído"
            first_item = self.columns["done"].task_list.item(0)
            if first_item:
                first_item.setBackground(QColor("#FFFFFF"))
                if hasattr(first_item, 'update_display'):
                    first_item.update_display()
                    first_item.ensure_visible()
        
        # Agendar uma atualização atrasada para garantir que todos os itens tenham fundo branco
        QTimer.singleShot(200, self.apply_white_background_to_all_items)
        QTimer.singleShot(500, self.apply_white_background_to_all_items)
        QTimer.singleShot(1000, self.apply_white_background_to_all_items)
    
    def apply_white_background_to_all_items(self):
        """Aplica fundo branco a todos os itens de todas as colunas"""
        if not hasattr(self, 'columns'):
            return
            
        for column_id, column in self.columns.items():
            if hasattr(column, 'task_list') and column.task_list:
                for i in range(column.task_list.count()):
                    item = column.task_list.item(i)
                    if item:
                        item.setBackground(QColor("#FFFFFF"))
                        if hasattr(item, 'update_display'):
                            item.update_display()
                        if hasattr(item, 'ensure_visible'):
                            item.ensure_visible()
                        
                # Força uma atualização visual
                column.task_list.repaint()
    
    def refresh_style(self):
        """Atualiza o estilo de todas as colunas e tarefas"""
        self.setStyleSheet("")  # Limpa o estilo
        self.setStyleSheet(KANBAN_STYLE)  # Reaplicar o estilo
        
        # Atualizar cada coluna
        for column_id, column in self.columns.items():
            # Força a atualização da aparência de todos os itens
            for i in range(column.task_list.count()):
                item = column.task_list.item(i)
                if item:
                    item.update_display() 
    
    def refresh_all_tasks(self):
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
                                
                # Especial para a primeira tarefa da coluna 'done'
                self.fix_done_column_first_item()
                
        except Exception as e:
            # Silenciosamente ignorar erros durante a atualização automática
            pass
    
    def fix_done_column_first_item(self):
        """Solução específica para o problema da primeira tarefa na coluna 'done'"""
        try:
            if hasattr(self, 'columns') and 'done' in self.columns:
                done_column = self.columns['done']
                if done_column.task_list.count() > 0:
                    # Garantir que o primeiro item tenha cor de fundo branca
                    first_item = done_column.task_list.item(0)
                    if first_item:
                        # Aplicar fundo branco e texto preto
                        first_item.setBackground(QColor("#FFFFFF"))
                        first_item.setForeground(QColor("#000000"))
                        
                        # Se for TaskItem, atualizar a aparência também
                        if isinstance(first_item, TaskItem):
                            first_item.update_display()
                            if hasattr(first_item, 'ensure_visible'):
                                first_item.ensure_visible()
                        
                        # Forçar atualização visual
                        done_column.task_list.repaint()
        except Exception:
            # Ignorar silenciosamente qualquer erro
            pass
    
    def save_all_tasks_to_db(self):
        """Salva todas as tarefas de todas as colunas no banco de dados"""
        try:
            if not hasattr(self, 'columns'):
                return False
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(DB_FILE)
            
            # Contador de tarefas salvas
            saved_count = 0
            
            # Para cada coluna, salvar suas tarefas
            for column_id, column in self.columns.items():
                if hasattr(column, 'get_all_tasks'):
                    tasks = column.get_all_tasks()
                    for task in tasks:
                        if 'id' in task:
                            # Garantir que a coluna no task seja a mesma do banco
                            task['column'] = column_id
                            
                            # Verificar se a tarefa já existe no banco
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task["id"],))
                            exists = cursor.fetchone() is not None
                            
                            if exists:
                                # Atualizar tarefa existente
                                cursor.execute(
                                    "UPDATE tasks SET title = ?, description = ?, priority = ?, column_id = ? WHERE id = ?",
                                    (
                                        task.get("title", ""),
                                        task.get("description", ""),
                                        task.get("priority", "Baixa"),
                                        task.get("column", column_id),
                                        task["id"]
                                    )
                                )
                            else:
                                # Inserir nova tarefa
                                cursor.execute(
                                    "INSERT INTO tasks (id, title, description, priority, column_id) VALUES (?, ?, ?, ?, ?)",
                                    (
                                        task["id"],
                                        task.get("title", ""),
                                        task.get("description", ""),
                                        task.get("priority", "Baixa"),
                                        task.get("column", column_id)
                                    )
                                )
                            
                            saved_count += 1
            
            # Commit das alterações
            conn.commit()
            conn.close()
            
            print(f"Total de {saved_count} tarefas salvas no banco de dados.")
            return True
            
        except Exception as e:
            print(f"Erro ao salvar todas as tarefas no banco: {str(e)}")
            # Tentar reverter a transação se falhar
            try:
                if conn:
                    conn.rollback()
                    conn.close()
            except:
                pass
            return False
    
    def save_all_tasks(self):
        """Salva todas as tarefas de todas as colunas"""
        # Chamar o método de salvamento no banco de dados
        return self.save_all_tasks_to_db()

    def add_task(self):
        """Adicionar nova tarefa através de um diálogo"""
        try:
            # Criar um diálogo para adicionar tarefa
            dialog = TaskDialog(self)
            result = dialog.exec_()
            
            if result:
                # Obter dados da tarefa do diálogo
                task_data = dialog.get_task_data()
                
                # Adicionar ID único se não existir
                if "id" not in task_data:
                    task_data["id"] = f"task_{int(time.time() * 1000)}"
                
                # Definir coluna inicial como "to_do"
                task_data["column"] = "to_do"
                
                # Adicionar a tarefa à coluna "to_do"
                if "to_do" in self.columns:
                    self.columns["to_do"].add_task_item(task_data)
                    self.unsaved_changes = True
                    return True
                else:
                    print("Erro: Coluna 'to_do' não encontrada")
        except Exception as e:
            print(f"Erro ao adicionar tarefa: {e}")
            import traceback
            traceback.print_exc()
        
        return False 