#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Cores da marca
PRIMARY_COLOR = "#1e88e5"  # Azul SnapDev
SECONDARY_COLOR = "#64b5f6"  # Azul claro SnapDev
ACCENT_COLOR = "#0d47a1"  # Azul escuro SnapDev
LIGHT_BG_COLOR = "#e3f2fd"  # Fundo azul muito claro

# Cores das colunas
TODO_COLOR = "#bbdefb"  # Azul claro para "A Fazer"
IN_PROGRESS_COLOR = "#fff9c4"  # Amarelo claro para "Em Progresso"
DONE_COLOR = "#c8e6c9"  # Verde claro para "Concluído"

# Prioridades
HIGH_PRIORITY_COLOR = "#f44336"  # Vermelho
MEDIUM_PRIORITY_COLOR = "#ff9800"  # Laranja
LOW_PRIORITY_COLOR = "#4caf50"  # Verde

# Nota: As bordas coloridas das colunas foram removidas, mantendo apenas os fundos coloridos
# e os títulos com texto preto sem fundo nem borda.

# Estilos específicos para corrigir o problema de transparência
FIXED_STYLES = '''
    QListWidget::item,
    QListWidget::item:selected,
    QListWidget::item:focus,
    QListWidget::item:hover {
        background-color: white !important;
        min-height: 60px !important;
    }
'''

# Estilos para a aplicação
MAIN_STYLE = f"""
    QMainWindow {{
        background-color: #f5f5f5;
    }}
    
    QWidget#header {{
        background-color: {PRIMARY_COLOR};
        color: white;
        padding: 8px;
        border-bottom: 1px solid #d0d0d0;
    }}
    
    QTabWidget::pane {{
        border: 1px solid #e0e0e0;
        background-color: white;
        border-radius: 3px;
    }}
    
    QTabBar::tab {{
        background-color: #e0e0e0;
        color: #404040;
        min-width: 100px;
        padding: 8px 15px;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: 1px solid #d0d0d0;
        border-bottom: none;
    }}
    
    QTabBar::tab:!selected {{
        margin-top: 2px;
    }}
    
    QPushButton {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
    }}
    
    QPushButton:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    
    QPushButton:pressed {{
        background-color: {ACCENT_COLOR};
    }}
    
    QLabel {{
        color: #404040;
    }}
    
    QLabel#header_title {{
        color: white;
        font-weight: bold;
        font-size: 16pt;
    }}
    
    QGroupBox {{
        border: 1px solid #e0e0e0;
        border-radius: 3px;
        margin-top: 10px;
        padding-top: 15px;
        background-color: white;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 5px;
        color: {PRIMARY_COLOR};
        background-color: white;
    }}
    
    QStatusBar {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
"""

# Estilos específicos para o Kanban
KANBAN_STYLE = f"""
    /* Estilo do quadro */
    QWidget#kanban_board {{
        background-color: #f9f9f9;
    }}
    
    /* Estilo das listas para as diferentes colunas */
    QListWidget[column="to_do"] {{
        background-color: {TODO_COLOR};
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 5px;
    }}
    
    QListWidget[column="doing"] {{
        background-color: {IN_PROGRESS_COLOR};
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 5px;
    }}
    
    QListWidget[column="done"] {{
        background-color: {DONE_COLOR};
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 5px;
    }}
    
    /* Estilo dos itens */
    QListWidget::item {{
        background-color: white;
        margin: 5px;
        padding: 12px;
        min-height: 80px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        color: #333333;
    }}
    
    /* Borda esquerda para os itens em cada coluna */
    QListWidget[column="to_do"]::item {{
        border-left: 5px solid #2196f3;
    }}
    
    QListWidget[column="doing"]::item {{
        border-left: 5px solid #ffc107;
    }}
    
    QListWidget[column="done"]::item {{
        border-left: 5px solid #4caf50;
    }}
    
    /* Estilo dos cabeçalhos de coluna - garantindo transparência */
    QLabel[column_header] {{
        color: black;
        background-color: transparent !important;
        border: none !important;
        font-weight: bold;
        font-size: 14pt;
    }}
    
    /* Estilo para o botão Adicionar */
    QPushButton#add_task_button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        font-weight: bold;
        padding: 8px 20px;
        border-radius: 4px;
        min-height: 35px;
        min-width: 120px;
    }}
    
    /* Estilo para o botão Salvar */
    QPushButton#save_button {{
        background-color: {LOW_PRIORITY_COLOR};
        color: white;
        font-weight: bold;
        padding: 10px 25px;
        border-radius: 4px;
        font-size: 11pt;
    }}
    
    /* Estilo para menus de contexto */
    QMenu {{
        background-color: white;
        color: #333333;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px;
    }}
    
    QMenu::item {{
        background-color: transparent;
        color: #333333;
        padding: 6px 25px;
        min-width: 150px;
    }}
    
    QMenu::item:selected {{
        background-color: #f0f0f0;
        color: #333333;
    }}
"""

# Estilos específicos para diálogos
DIALOG_STYLE = f"""
    QDialog {{
        background-color: transparent;
    }}
    
    QWidget#main_container {{
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 10px;
    }}
    
    QWidget#content_container {{
        background-color: white;
    }}
    
    QLabel {{
        font-size: 12pt;
        color: #333333;
        font-weight: normal;
    }}
    
    QLabel#field_label {{
        color: #555555;
        font-size: 11pt;
        font-weight: bold;
    }}
    
    QLineEdit, QTextEdit {{
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 14px;
        background-color: #f8f9fc;
        color: #333333;
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
        font-size: 12pt;
        min-height: 50px;
        line-height: 24px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
        background-color: white;
    }}
    
    QLineEdit:hover:!focus, QTextEdit:hover:!focus {{
        border: 1px solid #bbdefb;
    }}
    
    QLineEdit::placeholder, QTextEdit::placeholder {{
        color: #9e9e9e;
    }}
    
    QComboBox {{
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 14px;
        background-color: #f8f9fc;
        color: #333333;
        selection-background-color: {PRIMARY_COLOR};
        selection-color: white;
        font-size: 12pt;
        min-height: 50px;
        line-height: 24px;
    }}
    
    QComboBox:focus {{
        border: 2px solid {PRIMARY_COLOR};
        background-color: white;
    }}
    
    QComboBox:hover:!focus {{
        border: 1px solid #bbdefb;
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border-left: none;
        padding-right: 10px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 14px;
        height: 14px;
        background-color: {PRIMARY_COLOR};
        mask: url(down-arrow.png);
    }}
    
    QPushButton {{
        min-width: 120px;
        padding: 12px 25px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 11pt;
        color: white;
    }}
    
    QPushButton[text="Salvar"] {{
        background-color: {PRIMARY_COLOR};
        border: none;
    }}
    
    QPushButton[text="Salvar"]:hover {{
        background-color: #1976d2;
    }}
    
    QPushButton[text="Salvar"]:pressed {{
        background-color: {ACCENT_COLOR};
    }}
    
    QPushButton[text="Cancelar"] {{
        background-color: #f2f2f2;
        color: #555555;
        border: 1px solid #e0e0e0;
    }}
    
    QPushButton[text="Cancelar"]:hover {{
        background-color: #eeeeee;
    }}
    
    QPushButton[text="Cancelar"]:pressed {{
        background-color: #e0e0e0;
    }}
    
    QPushButton[text="Fechar"] {{
        background-color: #f2f2f2;
        color: #555555;
        border: 1px solid #e0e0e0;
    }}
    
    QPushButton[text="Fechar"]:hover {{
        background-color: #eeeeee;
    }}
    
    QPushButton[text="Fechar"]:pressed {{
        background-color: #e0e0e0;
    }}
    
    QPushButton[text="Editar"] {{
        background-color: {PRIMARY_COLOR};
        border: none;
    }}
    
    QPushButton[text="Editar"]:hover {{
        background-color: #1976d2;
    }}
    
    QPushButton[text="Editar"]:pressed {{
        background-color: {ACCENT_COLOR};
    }}
    
    QFormLayout {{
        spacing: 20px;
    }}
"""

# Estilo para menus de contexto
MENU_STYLE = f"""
    /* Estilo para menus de contexto */
    QMenu {{
        background-color: white;
        color: #333333;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px;
    }}
    
    QMenu::item {{
        background-color: transparent;
        color: #333333;
        padding: 6px 25px;
        min-width: 150px;
    }}
    
    QMenu::item:selected {{
        background-color: #f0f0f0;
        color: #333333;
    }}
"""
