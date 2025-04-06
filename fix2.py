#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Este script cria um arquivo de estilo QSS dedicado para resolver o problema 
de transparência nas tarefas do Kanban. Ele sobrescreve completamente os estilos
anteriores para garantir que os itens nunca fiquem transparentes.
"""

import os

# Nome do arquivo de estilo a ser criado
STYLE_QSS_FILE = os.path.join("app", "utils", "kanban_fix.qss")

# Caminho para o arquivo kanban_board.py
KANBAN_BOARD_FILE = os.path.join("app", "components", "kanban_board.py")

def create_qss_file():
    """Cria um arquivo QSS dedicado com estilos para corrigir o problema"""
    
    QSS_CONTENT = """
/* Estilos fixos para o quadro Kanban */

/* Colunas */
QWidget[column_id="to_do"] {
    background-color: #bbdefb;
    border: 2px solid #2196f3;
    border-radius: 5px;
}

QWidget[column_id="doing"] {
    background-color: #fff9c4;
    border: 2px solid #ffc107;
    border-radius: 5px;
}

QWidget[column_id="done"] {
    background-color: #c8e6c9;
    border: 2px solid #4caf50;
    border-radius: 5px;
}

/* Listas de tarefas */
QListWidget[column="to_do"] {
    background-color: #bbdefb;
    border: 1px solid #2196f3;
    border-radius: 3px;
    padding: 5px;
}

QListWidget[column="doing"] {
    background-color: #fff9c4;
    border: 1px solid #ffc107;
    border-radius: 3px;
    padding: 5px;
}

QListWidget[column="done"] {
    background-color: #c8e6c9;
    border: 1px solid #4caf50;
    border-radius: 3px;
    padding: 5px;
}

/* Estilo dos itens - sempre branco */
QListWidget::item {
    background-color: white !important;
    border-top: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
    border-radius: 3px;
    padding: 5px;
    margin: 5px;
    color: black;
    font-weight: bold;
}

/* Itens por coluna - ajusta apenas a borda esquerda */
QListWidget[column="to_do"]::item {
    border-left: 5px solid #2196f3;
}

QListWidget[column="doing"]::item {
    border-left: 5px solid #ffc107;
}

QListWidget[column="done"]::item {
    border-left: 5px solid #4caf50;
}

/* Estados de seleção */
QListWidget::item:selected,
QListWidget::item:hover,
QListWidget::item:focus {
    background-color: white !important;
    border: 1px solid #bbbbbb;
    color: black;
}

QListWidget[column="to_do"]::item:selected,
QListWidget[column="to_do"]::item:hover,
QListWidget[column="to_do"]::item:focus {
    border-left: 5px solid #2196f3;
}

QListWidget[column="doing"]::item:selected,
QListWidget[column="doing"]::item:hover,
QListWidget[column="doing"]::item:focus {
    border-left: 5px solid #ffc107;
}

QListWidget[column="done"]::item:selected,
QListWidget[column="done"]::item:hover,
QListWidget[column="done"]::item:focus {
    border-left: 5px solid #4caf50;
}
"""
    
    # Cria o arquivo QSS
    with open(STYLE_QSS_FILE, 'w', encoding='utf-8') as file:
        file.write(QSS_CONTENT)
    
    print(f"✅ Arquivo QSS criado com sucesso: {STYLE_QSS_FILE}")
    return True

def modify_kanban_board():
    """Modifica o arquivo kanban_board.py para carregar o QSS personalizado"""
    
    if not os.path.exists(KANBAN_BOARD_FILE):
        print(f"Erro: Arquivo kanban_board.py não encontrado: {KANBAN_BOARD_FILE}")
        return False
    
    # Ler o conteúdo atual
    with open(KANBAN_BOARD_FILE, 'r', encoding='utf-8') as file:
        content = file.readlines()
    
    # Função para carregar o QSS no código
    LOAD_QSS_CODE = """    def load_qss_file(self):
        """Carrega o arquivo QSS para corrigir estilos"""
        try:
            qss_file = os.path.join("app", "utils", "kanban_fix.qss")
            if os.path.exists(qss_file):
                with open(qss_file, 'r', encoding='utf-8') as file:
                    style = file.read()
                    self.setStyleSheet(style)
                    # Aplicar também nas colunas
                    for column_id, column in self.columns.items():
                        column.setStyleSheet(style)
                print("✅ Estilos QSS carregados com sucesso!")
                return True
            else:
                print(f"❌ Arquivo QSS não encontrado: {qss_file}")
                return False
        except Exception as e:
            print(f"❌ Erro ao carregar QSS: {str(e)}")
            return False

"""
    
    # Modificação na função __init__ para carregar o QSS
    import_line_added = False
    init_modified = False
    load_qss_added = False
    
    # Novas linhas para o arquivo
    new_content = []
    
    for line in content:
        # Adicionar às novas linhas
        new_content.append(line)
        
        # Verificar se é a linha de importação para adicionar 'QFile, QTextStream'
        if not import_line_added and "from PySide6.QtCore import" in line:
            import_line_added = True
        
        # Verificar se é o final da função load_columns para adicionar a chamada ao QSS
        if not init_modified and "def load_columns(self):" in line:
            # Procurar a linha que adiciona o layout de colunas ao layout principal
            for i, next_line in enumerate(content):
                if "self.main_layout.addLayout(column_layout)" in next_line:
                    # Adicionar a chamada ao carregar QSS logo após a linha
                    modified_line = next_line + "\n        # Aplicar estilos QSS para corrigir transparência\n        self.load_qss_file()\n"
                    # Substituir a linha original pela modificada
                    new_content[new_content.index(next_line)] = modified_line
                    init_modified = True
                    break
        
        # Adicionar a função load_qss_file antes da função refresh_style
        if not load_qss_added and "def refresh_style(self):" in line:
            new_content.insert(new_content.index(line), LOAD_QSS_CODE)
            load_qss_added = True
    
    # Salvar o arquivo modificado
    with open(KANBAN_BOARD_FILE, 'w', encoding='utf-8') as file:
        file.writelines(new_content)
    
    print(f"✅ Arquivo kanban_board.py modificado com sucesso!")
    return True

def main():
    """Função principal"""
    print("🔧 Iniciando correção drástica de estilos do Kanban...")
    
    # Criar arquivo QSS
    create_qss_file()
    
    # Modificar arquivo kanban_board.py
    modify_kanban_board()
    
    print("✨ Concluído! Execute o aplicativo novamente para ver as mudanças.")
    print("💡 Dica: Se ainda houver problemas, tente deletar o arquivo tasks.db e reiniciar o aplicativo.")

if __name__ == "__main__":
    main() 