import os
import webbrowser
import threading
import sys
from flask import Flask, render_template, jsonify, request, send_from_directory
import webview
import time

# Verificar se estamos em modo de desenvolvimento ou executável
if getattr(sys, 'frozen', False):
    # Estamos executando em um executável bundled (PyInstaller)
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    base_dir = sys._MEIPASS
else:
    # Estamos executando em modo de desenvolvimento
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))

# Configurar rotas da aplicação
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'img/icon.png', mimetype='image/png')

# API para salvar dados
@app.route('/api/save', methods=['POST'])
def save_data():
    data = request.json
    # Em uma aplicação real, você salvaria em um arquivo ou banco de dados
    # Para um exemplo simples, apenas retornamos sucesso
    return jsonify({"success": True})

# API para carregar dados
@app.route('/api/load', methods=['GET'])
def load_data():
    # Em uma aplicação real, você carregaria de um arquivo ou banco de dados
    # Este é um exemplo de dados de demonstração
    return jsonify({
        "tasks": [
            {"id": 1, "title": "Criar documentação", "description": "Escrever documentação completa", "status": "todo", "priority": "medium"},
            {"id": 2, "title": "Implementar API", "description": "Desenvolver endpoints RESTful", "status": "in-progress", "priority": "high"},
            {"id": 3, "title": "Corrigir bug #123", "description": "Resolver problema na tela de login", "status": "done", "priority": "high"}
        ],
        "pomodoro": {
            "workTime": 25,
            "breakTime": 5
        }
    })

def start_server():
    app.run(port=5000, debug=False)

def open_webview():
    # Esperar o servidor iniciar
    time.sleep(1)
    # Abrir a janela webview
    webview.create_window("SnapDev Task - Sistema Kanban", 
                          "http://localhost:5000",
                          width=1200, 
                          height=800,
                          min_size=(800, 600), 
                          icon=os.path.join(base_dir, 'static', 'img', 'icon.png'))
    webview.start()
    # Encerrar o aplicativo quando a janela for fechada
    os._exit(0)

if __name__ == '__main__':
    # Iniciar o servidor Flask em uma thread separada
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Iniciar a aplicação webview
    webview_thread = threading.Thread(target=open_webview)
    webview_thread.start()
    
    try:
        # Manter a thread principal viva
        server_thread.join()
    except KeyboardInterrupt:
        sys.exit(0) 