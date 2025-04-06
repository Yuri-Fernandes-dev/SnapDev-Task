#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.components.main_window import MainWindow


def main():
    """Função principal da aplicação"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo consistente em todas as plataformas
    
    # Configurar ícone da aplicação
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 