#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap

from app.components.kanban_board import KanbanBoard
from app.components.pomodoro_timer import PomodoroTimer
from app.utils.style import MAIN_STYLE, KANBAN_STYLE, DIALOG_STYLE


class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        
        # Configurar janela principal
        self.setWindowTitle("Gerenciador de Tarefas")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Aplicar estilos
        self.setStyleSheet(MAIN_STYLE)
        
        # Criar e definir o widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Barra de cabeçalho
        header_widget = QWidget()
        header_widget.setObjectName("header")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)  # Adicionar padding interno
        
        # Logo (maior)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'EsteLogo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            header_layout.addWidget(logo_label)
        
        # Título
        header_label = QLabel("SnapDev Task")
        header_label.setObjectName("header_title")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Botões de ação
        self.pomodoro_button = QPushButton("Iniciar Pomodoro")
        self.pomodoro_button.setFixedWidth(150)
        self.pomodoro_button.setStyleSheet("""
            background-color: white;
            color: #1e88e5;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
        """)
        self.pomodoro_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1e88e5;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 1px solid #bbdefb;
            }
        """)
        header_layout.addWidget(self.pomodoro_button)
        
        self.layout.addWidget(header_widget)
        
        # Conteúdo principal em um widget separado com margens
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Abas
        self.tabs = QTabWidget()
        content_layout.addWidget(self.tabs)
        
        # Aba Kanban
        self.kanban_board = KanbanBoard(self)
        self.tabs.addTab(self.kanban_board, "Quadro Kanban")
        
        # Aba Pomodoro
        self.pomodoro_timer = PomodoroTimer()
        self.tabs.addTab(self.pomodoro_timer, "Pomodoro")
        
        self.layout.addWidget(content_widget)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("SnapDev Task - Gerencie suas tarefas com eficiência")
        
        # Conexões
        self.pomodoro_button.clicked.connect(self._toggle_pomodoro)
        
        # Estilo das guias
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(True)
        
    def _toggle_pomodoro(self):
        """Alterna para a aba do Pomodoro e inicia/pausa o timer"""
        self.tabs.setCurrentWidget(self.pomodoro_timer)
        self.pomodoro_timer.toggle_timer()

    def closeEvent(self, event):
        """Sobrescreve o evento de fechamento para confirmar com o usuário"""
        reply = QMessageBox.question(
            self, 
            "Sair", 
            "Deseja salvar as tarefas antes de sair?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            # Salvar e sair
            if self.kanban_board.save_all_tasks():
                event.accept()
            else:
                # Se falhar ao salvar, perguntar se deseja sair mesmo assim
                force_exit = QMessageBox.question(
                    self, 
                    "Erro ao Salvar", 
                    "Ocorreu um erro ao salvar. Deseja sair mesmo assim?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if force_exit == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
        elif reply == QMessageBox.No:
            # Sair sem salvar
            event.accept()
        else:
            # Cancelar fechamento
            event.ignore() 