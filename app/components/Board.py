    def add_task(self):
        # Cria um diálogo simples para adicionar tarefa
        dialog = TaskDialog(self)
        result = dialog.exec_()
        
        if result:
            try:
                # Obter dados da tarefa do diálogo
                task_data = dialog.get_task_data()
                
                # Adicionar a tarefa à coluna "to_do"
                column = "to_do"
                self.add_task_item(task_data, column)
                
            except Exception as e:
                print(f"Erro ao adicionar tarefa: {e}")

    def add_task_item(self, task_data, column):
        # Cria um item de tarefa e adiciona à coluna apropriada
        try:
            item = TaskItem(task_data)
            list_widget = self.columns[column]
            list_widget.addItem(item)
            list_widget.setItemWidget(item, item.widget)
            self.unsaved_changes = True
        except Exception as e:
            print(f"Erro ao adicionar item: {e}") 