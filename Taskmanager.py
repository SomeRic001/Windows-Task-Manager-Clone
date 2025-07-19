import psutil
from Tasks import Tasks
import sys
from PyQt5.QtCore import QSize, Qt,QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, 
    QTableWidgetItem, QDockWidget, QFormLayout, 
    QLineEdit, QWidget, QPushButton, QSpinBox, 
    QMessageBox, QToolBar, QMessageBox,QTreeWidget,
    QTreeWidgetItem,QWidget,QVBoxLayout,QHBoxLayout
)
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.total_proc=0
        self.totalmem_per = 0
        self.totalcpu = 0

    def processes(self):
        num = 1
        for proc in psutil.process_iter():
            pid = proc.pid
            name = proc.name()
            if name.lower() == "system idle process" :
                continue
            memory = round((proc.memory_info().rss)/(1024*1024),3)
            cpu = proc.cpu_percent(interval = 0)/psutil.cpu_count()
            self.process = Tasks(num,name,pid,memory,cpu)
            self.total_proc+=1
            self.totalmem_per += proc.memory_percent()
            self.totalcpu +=cpu
            self.tasks.append(self.process.stpr())
            num+=1
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.setWindowTitle("Process Manager")
        self.setGeometry(100,100,480,720)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.tree = QTreeWidget(self)
        self.fill_processes()
        self.pid_column_index = 4
        self.tree.itemClicked.connect(self.get_pid)
        self.main_layout.addWidget(self.tree)
        self.button_layout = QHBoxLayout()
        self.refresh_task = QPushButton("Refresh Tasks")
        self.end_task = QPushButton("End Task")
        self.force_end = QPushButton("Force End")
        self.button_layout.addWidget(self.end_task)
        self.button_layout.addWidget(self.refresh_task)
        self.button_layout.addWidget(self.force_end)
        self.refresh_task.clicked.connect(self.on_button_click)
        self.end_task.clicked.connect(self.kill_task)
        self.force_end.clicked.connect(self.force_kill)
        self.main_layout.addLayout(self.button_layout)
        self.timer.singleShot(1000,self.fill_processes)
       
    def fill_processes(self):
        self.T = TaskManager()
        self.T.processes()
        self.tree.setColumnCount(4)
        self.tree.clear()
        headerlabels = self.T.tasks[0].keys()
        self.tree.setHeaderLabels(headerlabels)
        for task in self.T.tasks:
            task_item = QTreeWidgetItem(self.tree)
            for col_index,key in enumerate(headerlabels):
                task_item.setText(col_index,str(task.get(key,"")))
    
    def get_pid(self,item,column):
        p_id = item.text(self.pid_column_index)
        self.id = int(p_id)
    
    def on_button_click(self):
        self.fill_processes()
    
    def kill_task(self):
        if hasattr(self,'id'):
            try:
                proc = psutil.Process(self.id)
                proc.terminate()
                self.fill_processes()
            except Exception as e:
                print("Failed to end process",e)
        else:
           QMessageBox.information(
               self,
               'Error ',
               'No Process Selected.'
           )
           
    def force_kill(self):
        if hasattr(self,'id'):
            try:
                proc = psutil.Process(self.id)
                proc.kill()
                self.fill_processes()
            except Exception as e:
                print("Failed to kill process",e)
        else:
           QMessageBox.information(
               self,
               'Error ',
               'No Process Selected.'
           )
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
