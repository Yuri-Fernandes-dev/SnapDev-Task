#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QProgressBar, QSlider, QSpinBox,
    QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

class CircularProgressBar(QProgressBar):
    """Barra de progresso circular personalizada para o Pomodoro"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(300, 300)
        
        # Estilo personalizado - apenas mostrar os números sem animação de preenchimento
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #1e88e5;
                border-radius: 150px;
                background-color: #f0f0f0;
                text-align: center;
                font-size: 60px;
                font-weight: bold;
                color: #1e88e5;
            }
            
            QProgressBar::chunk {
                background-color: transparent;
            }
        """)
        
    def update_time_display(self, minutes, seconds):
        """Atualiza apenas o texto sem usar o setValue"""
        self.setFormat(f"{minutes:02d}:{seconds:02d}")
        # Mantém o valor no mínimo para não mostrar progresso
        self.setValue(0)


class PomodoroTimer(QWidget):
    """Temporizador Pomodoro"""
    
    # Sinais
    timer_complete = Signal(str)  # tipo de timer concluído
    
    # Configurações padrão
    DEFAULT_WORK_TIME = 25  # minutos
    DEFAULT_SHORT_BREAK = 5  # minutos
    DEFAULT_LONG_BREAK = 15  # minutos
    POMODOROS_UNTIL_LONG_BREAK = 4
    
    # Estados do Pomodoro
    IDLE = 0
    WORKING = 1
    SHORT_BREAK = 2
    LONG_BREAK = 3
    
    # Cores principais
    SNAPDEV_BLUE = "#1e88e5"  # Azul principal
    SNAPDEV_ORANGE = "#f57c00"  # Laranja
    SNAPDEV_RED = "#e53935"  # Vermelho
    SNAPDEV_GREEN = "#43a047"  # Verde
    SNAPDEV_PURPLE = "#8e24aa"  # Roxo
    
    # Cores de estado
    WORK_COLOR = "#1e88e5"   # Azul para trabalho
    SHORT_BREAK_COLOR = "#43a047"  # Verde para pausa curta
    LONG_BREAK_COLOR = "#f57c00"   # Laranja para pausa longa
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurações
        self.work_time = self.DEFAULT_WORK_TIME
        self.short_break = self.DEFAULT_SHORT_BREAK
        self.long_break = self.DEFAULT_LONG_BREAK
        
        # Estado
        self.state = self.IDLE
        self.remaining_seconds = 0
        self.pomodoro_count = 0
        
        # Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 1 segundo
        self.timer.timeout.connect(self.update_timer)
        
        # Configuração do som de alarme
        self.alarm_sound = QSoundEffect()
        alarm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'alarme.wav')
        if os.path.exists(alarm_path):
            self.alarm_sound.setSource(QUrl.fromLocalFile(alarm_path))
            self.alarm_sound.setVolume(0.8)
        
        # Estilo personalizado para o Pomodoro
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #ffffff;
                color: {self.SNAPDEV_BLUE};
            }}
            
            QLabel#title {{
                color: {self.SNAPDEV_BLUE};
                font-size: 16pt;
                font-weight: bold;
            }}
            
            QLabel#counter {{
                color: {self.SNAPDEV_PURPLE};
                font-size: 14pt;
            }}
            
            QLabel#status {{
                color: {self.SNAPDEV_BLUE};
                font-size: 14pt;
                font-weight: bold;
            }}
            
            QPushButton {{
                min-width: 120px;
                padding: 8px 15px;
            }}
            
            QPushButton#start {{
                background-color: {self.SNAPDEV_BLUE};
                color: white;
            }}
            
            QPushButton#start:hover {{
                background-color: #64b5f6;
            }}
            
            QPushButton#reset {{
                background-color: {self.SNAPDEV_ORANGE};
                color: white;
            }}
            
            QPushButton#reset:hover {{
                background-color: #ffb74d;
            }}
            
            QPushButton#skip {{
                background-color: {self.SNAPDEV_RED};
                color: white;
            }}
            
            QPushButton#skip:hover {{
                background-color: #ef5350;
            }}
            
            QSpinBox {{
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                padding: 3px;
                min-width: 70px;
            }}
            
            QLabel[type="config"] {{
                color: {self.SNAPDEV_BLUE};
                font-weight: bold;
            }}
        """)
        
        # Configurar UI
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title_label = QLabel("Técnica Pomodoro")
        title_label.setObjectName("title")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Contador de pomodoros
        self.pomodoro_counter = QLabel("Pomodoros: 0")
        self.pomodoro_counter.setObjectName("counter")
        self.pomodoro_counter.setFont(QFont("Arial", 12))
        header_layout.addWidget(self.pomodoro_counter)
        
        layout.addLayout(header_layout)
        
        # Barra de progresso circular
        progress_layout = QHBoxLayout()
        progress_layout.addStretch()
        
        self.progress_bar = CircularProgressBar()
        self.progress_bar.update_time_display(self.work_time, 0)  # Inicializar com o tempo de trabalho
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        
        layout.addLayout(progress_layout)
        
        # Status atual
        self.status_label = QLabel("Pronto para começar")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.status_label)
        
        # Controles
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        self.start_button = QPushButton("Iniciar")
        self.start_button.setObjectName("start")
        self.start_button.setMinimumWidth(100)
        self.start_button.clicked.connect(self.toggle_timer)
        controls_layout.addWidget(self.start_button)
        
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.setObjectName("reset")
        self.reset_button.setMinimumWidth(100)
        self.reset_button.clicked.connect(self.reset_timer)
        controls_layout.addWidget(self.reset_button)
        
        self.skip_button = QPushButton("Pular")
        self.skip_button.setObjectName("skip")
        self.skip_button.setMinimumWidth(100)
        self.skip_button.clicked.connect(self.skip_phase)
        controls_layout.addWidget(self.skip_button)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Configurações
        settings_group = QGroupBox("Configurações")
        settings_layout = QHBoxLayout(settings_group)
        
        # Tempo de trabalho
        work_layout = QVBoxLayout()
        work_label = QLabel("Trabalho (min)")
        work_label.setProperty("type", "config")
        work_layout.addWidget(work_label)
        
        self.work_spinner = QSpinBox()
        self.work_spinner.setMinimum(1)
        self.work_spinner.setMaximum(60)
        self.work_spinner.setValue(self.work_time)
        self.work_spinner.valueChanged.connect(self.update_settings)
        work_layout.addWidget(self.work_spinner)
        
        settings_layout.addLayout(work_layout)
        
        # Pausa curta
        short_break_layout = QVBoxLayout()
        short_break_label = QLabel("Pausa curta (min)")
        short_break_label.setProperty("type", "config")
        short_break_layout.addWidget(short_break_label)
        
        self.short_break_spinner = QSpinBox()
        self.short_break_spinner.setMinimum(1)
        self.short_break_spinner.setMaximum(30)
        self.short_break_spinner.setValue(self.short_break)
        self.short_break_spinner.valueChanged.connect(self.update_settings)
        short_break_layout.addWidget(self.short_break_spinner)
        
        settings_layout.addLayout(short_break_layout)
        
        # Pausa longa
        long_break_layout = QVBoxLayout()
        long_break_label = QLabel("Pausa longa (min)")
        long_break_label.setProperty("type", "config")
        long_break_layout.addWidget(long_break_label)
        
        self.long_break_spinner = QSpinBox()
        self.long_break_spinner.setMinimum(1)
        self.long_break_spinner.setMaximum(60)
        self.long_break_spinner.setValue(self.long_break)
        self.long_break_spinner.valueChanged.connect(self.update_settings)
        long_break_layout.addWidget(self.long_break_spinner)
        
        settings_layout.addLayout(long_break_layout)
        
        # Opção de som
        sound_layout = QVBoxLayout()
        sound_label = QLabel("Som")
        sound_label.setProperty("type", "config")
        sound_layout.addWidget(sound_label)
        
        self.sound_check = QCheckBox("Alarme sonoro")
        self.sound_check.setChecked(True)
        sound_layout.addWidget(self.sound_check)
        
        settings_layout.addLayout(sound_layout)
        
        layout.addWidget(settings_group)
        
        # Inicializar o timer
        self.setup_next_phase()
    
    def toggle_timer(self):
        """Inicia ou pausa o temporizador"""
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setText("Continuar")
            self.status_label.setText("Em pausa")
        else:
            if self.state == self.IDLE:
                self.setup_next_phase()
            
            self.timer.start()
            self.start_button.setText("Pausar")
            
            # Atualizar status
            if self.state == self.WORKING:
                self.status_label.setText("Trabalhando")
            elif self.state == self.SHORT_BREAK:
                self.status_label.setText("Pausa curta")
            elif self.state == self.LONG_BREAK:
                self.status_label.setText("Pausa longa")
    
    def reset_timer(self):
        """Reinicia o temporizador para o início da fase atual"""
        self.timer.stop()
        self.setup_current_phase()
        self.start_button.setText("Iniciar")
        self.status_label.setText("Reiniciado")
    
    def update_timer(self):
        """Atualiza o temporizador a cada segundo"""
        if self.remaining_seconds <= 0:
            self.timer_completed()
            return
        
        self.remaining_seconds -= 1
        self.update_display()
    
    def update_display(self):
        """Atualiza a exibição do temporizador"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        
        # Usar o novo método para atualizar apenas o texto
        self.progress_bar.update_time_display(minutes, seconds)
    
    def timer_completed(self):
        """Manipula a conclusão do temporizador"""
        self.timer.stop()
        
        # Tocar som de alarme
        if self.sound_check.isChecked() and self.alarm_sound.isLoaded():
            self.alarm_sound.play()
        
        # Emitir sinal de conclusão
        if self.state == self.WORKING:
            self.pomodoro_count += 1
            self.pomodoro_counter.setText(f"Pomodoros: {self.pomodoro_count}")
            self.timer_complete.emit("work")
        elif self.state == self.SHORT_BREAK:
            self.timer_complete.emit("short_break")
        elif self.state == self.LONG_BREAK:
            self.timer_complete.emit("long_break")
        
        # Configurar próxima fase
        self.setup_next_phase()
        
        # Atualizar interface
        self.start_button.setText("Iniciar")
    
    def setup_next_phase(self):
        """Configura a próxima fase do Pomodoro"""
        # Determinar próxima fase
        if self.state == self.IDLE or self.state == self.SHORT_BREAK or self.state == self.LONG_BREAK:
            # Próxima fase é trabalho
            self.state = self.WORKING
            self.remaining_seconds = self.work_time * 60
            self.status_label.setText("Pronto para trabalhar")
        elif self.state == self.WORKING:
            # Verificar se é hora de pausa longa
            if self.pomodoro_count % self.POMODOROS_UNTIL_LONG_BREAK == 0:
                self.state = self.LONG_BREAK
                self.remaining_seconds = self.long_break * 60
                self.status_label.setText("Pronto para pausa longa")
            else:
                self.state = self.SHORT_BREAK
                self.remaining_seconds = self.short_break * 60
                self.status_label.setText("Pronto para pausa curta")
        
        # Atualizar display
        self.update_display()
    
    def setup_current_phase(self):
        """Configura novamente a fase atual do Pomodoro"""
        if self.state == self.WORKING:
            self.remaining_seconds = self.work_time * 60
        elif self.state == self.SHORT_BREAK:
            self.remaining_seconds = self.short_break * 60
        elif self.state == self.LONG_BREAK:
            self.remaining_seconds = self.long_break * 60
        
        # Atualizar display
        self.update_display()
    
    def skip_phase(self):
        """Pula a fase atual para a próxima"""
        self.timer.stop()
        self.setup_next_phase()
        self.start_button.setText("Iniciar")
    
    def update_settings(self):
        """Atualiza as configurações do temporizador"""
        self.work_time = self.work_spinner.value()
        self.short_break = self.short_break_spinner.value()
        self.long_break = self.long_break_spinner.value()
        
        # Se estiver no estado parado, atualizar o display
        if not self.timer.isActive():
            self.setup_current_phase() 