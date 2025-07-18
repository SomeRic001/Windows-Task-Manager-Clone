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
            process = Tasks(num,name,pid,memory,cpu)
            self.total_proc+=1
            self.totalmem_per += proc.memory_percent()
            self.totalcpu +=cpu
            self.tasks.append(process.stpr())
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
        self.main_layout.addWidget(self.tree)
        self.button_layout = QHBoxLayout()
        self.refresh_task = QPushButton("Refresh Tasks")
        self.end_task = QPushButton("End Task")
        self.button_layout.addWidget(self.end_task)
        self.button_layout.addWidget(self.refresh_task)
        self.refresh_task.clicked.connect(self.on_button_click)
        self.main_layout.addLayout(self.button_layout)
        self.timer.singleShot(1000,self.fill_processes)
       
    def fill_processes(self):
        self.T = TaskManager()
        self.T.processes()
        self.tree.setColumnCount(4)
        headerlabels = self.T.tasks[0].keys()
        self.tree.setHeaderLabels(headerlabels)
        for task in self.T.tasks:
            task_item = QTreeWidgetItem(self.tree)
            for col_index,key in enumerate(headerlabels):
                task_item.setText(col_index,str(task.get(key,"")))
        
    
    def on_button_click(self):
        self.fill_processes()

    
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
