# Sistema de Tarefas Kanban com Pomodoro

Um aplicativo de gerenciamento de tarefas com metodologia Kanban e temporizador Pomodoro integrado.

## Requisitos

- Python 3.8+
- PySide6

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

Para iniciar o aplicativo, execute:

```bash
python run.py
```

Ou alternativamente:

```bash
python -m app.main
```

## Funcionalidades

- Sistema de tarefas usando metodologia Kanban (A Fazer, Em Progresso, Concluído)
- Timer Pomodoro para gerenciamento de tempo
- Interface gráfica intuitiva em português
- Personalizações dos tempos de trabalho e pausas
- Salvamento automático das tarefas

## Uso

### Quadro Kanban
- Adicione tarefas clicando no botão "+" na coluna "A Fazer"
- Arraste tarefas entre colunas ou use o menu de contexto (clique direito)
- Edite ou exclua tarefas pelo menu de contexto

### Pomodoro
- Configure os tempos de trabalho e pausas
- Use os botões para iniciar, pausar, reiniciar ou pular fases
- Acompanhe o progresso pela barra circular e contador de pomodoros 