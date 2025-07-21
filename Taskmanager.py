import psutil
import time
from Tasks import Tasks
import subprocess
import sys
from PyQt5.QtCore import QSize, Qt,QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, 
    QTableWidgetItem, QDockWidget, QFormLayout, 
    QLineEdit, QWidget, QPushButton, QSpinBox, 
    QMessageBox, QToolBar, QMessageBox,QTreeWidget,
    QTreeWidgetItem,QWidget,QVBoxLayout,QHBoxLayout,
    QLabel,QGridLayout,QInputDialog
)
import pyqtgraph as pg
class TaskManager:
    def __init__(self):
        self.tasks = []

    def processes(self):
        num = 1
        for proc in psutil.process_iter():
            pid = proc.pid
            name = proc.name()
            if name.lower() == "system idle process" :
                continue
            try:
                memory = round((proc.memory_info().rss)/(1024*1024),3)
            except (psutil.NoSuchProcess,psutil.AccessDenied,psutil.ZombieProcess):
                continue
            cpu = proc.cpu_percent(interval = 0)/psutil.cpu_count()
            self.process = Tasks(0,name,pid,memory,cpu)
            self.tasks.append(self.process.stpr())
        self.tasks.sort(key = lambda x:x['Process'].lower())
        num = 1
        for task in self.tasks:
            task['S.N.'] = num
            num+=1
            
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Initializing timers
        self.timer = QTimer()
        self.process_timer = QTimer(self)
        self.graph_timer = QTimer(self)
        #Setting up window
        self.setWindowTitle("Process Manager")
        self.setFixedSize(800,1000)
        #Widgets and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.performance_layout = QVBoxLayout()
        self.CPU_data = []
        self.mem_data = []
        self.CPU_label = QLabel(f"Total CPU Usage: {str(psutil.cpu_percent())}%")
        self.memory_label = QLabel(f"Total Memory Usage: {str(psutil.virtual_memory().percent)}%")
        self.new_task_button = QPushButton("Run New Process")
        self.new_task_button.clicked.connect(self.run_task)
        self.performance_layout.addWidget(self.CPU_label)
        self.performance_layout.addWidget(self.memory_label)
        self.performance_layout.addWidget(self.new_task_button)
        self.main_layout.addLayout(self.performance_layout)
        self.total_data_layout = QVBoxLayout()
        #Main Table/Tree
        self.tree = QTreeWidget(self)
        self.pid_column_index = 4
        self.fill_processes()
        self.tree.itemClicked.connect(self.get_pid)
        self.main_layout.addWidget(self.tree,stretch=4)
        #Process Timer for Updating Process
        self.process_timer.timeout.connect(self.fill_processes)
        self.process_timer.start(5000)
        #Buttons
        self.button_layout = QHBoxLayout()
        self.refresh_task = QPushButton("Refresh Process List")
        self.end_task = QPushButton("End Process")
        self.force_end = QPushButton("Force End")
        self.button_layout.addWidget(self.end_task)
        self.button_layout.addWidget(self.refresh_task)
        self.button_layout.addWidget(self.force_end)
        self.refresh_task.clicked.connect(self.on_button_click)
        self.end_task.clicked.connect(self.kill_task)
        self.force_end.clicked.connect(self.force_kill)
        self.main_layout.addLayout(self.button_layout)
        self.timer.singleShot(1000,self.fill_processes)
        #Graph Layout
        self.graph_widget = QWidget()
        self.graph_layout = QGridLayout()
        self.graph_widget.setLayout(self.graph_layout)
        pg.setConfigOption('background',"#f0f0f0c9")
        pg.setConfigOption('foreground','k')
        self.cpu_plot = self.createplot("CPU Usage(%):",(0,100),"r")
        self.memory_plot = self.createplot("Memory Usage(%):",(0,100),'g')
        self.graph_layout.addWidget(self.memory_plot,0,0)
        self.graph_layout.addWidget(self.cpu_plot,0,2)
        self.main_layout.addWidget(self.graph_widget,stretch=3)
        #Graph Timer for Updating Graph and Performance Stats
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(2000)

    def fill_processes(self):
        self.T = TaskManager()
        self.T.processes()
        self.tree.setColumnCount(5)
        headerlabels = self.T.tasks[0].keys()
        root = self.tree.invisibleRootItem()
        while (root.childCount() > 0):
            root.removeChild(root.child(0))
        self.tree.setHeaderLabels(headerlabels)
        for task in self.T.tasks:
            task_item = QTreeWidgetItem(self.tree)
            for col_index,key in enumerate(headerlabels):
                task_item.setText(col_index,str(task.get(key,"")))
    
    def update_graphs(self):
        #CPU
        cpu_percent = psutil.cpu_percent()
        self.CPU_data.append(cpu_percent)
        self.cpu_plot.getPlotItem().listDataItems()[0].setData(list(self.CPU_data))
        self.CPU_label.setText(f"Total CPU Usage: {str(cpu_percent)}%")
        #Memory
        memory_percent = psutil.virtual_memory().percent
        self.mem_data.append(memory_percent)
        self.memory_plot.getPlotItem().listDataItems()[0].setData(list(self.mem_data))
        self.memory_label.setText(f"Total Memory Usage: {str(memory_percent)} %")


    def get_pid(self,item,column):
        p_id = item.text(self.pid_column_index)
        self.id = int(p_id)
    
    def on_button_click(self):
        self.fill_processes()
    
    def run_task(self):
        cmd,ok = QInputDialog.getText(self,"Run New Process","Enter Process:")
        if ok and cmd.strip():
            try:
                subprocess.Popen([cmd.strip()])
                time.sleep(0.2)
                self.fill_processes()
            except FileNotFoundError:
                QMessageBox.information(
                    self,
                    'Error',
                    'No Such Program Found.'
                )
            except Exception as e:
                QMessageBox.information(
                    self,
                    'Error',
                    'Cant Open Proess.'
                )

    def kill_task(self):
        if hasattr(self,'id'):
            try:
                proc = psutil.Process(self.id)
                proc.terminate()
                time.sleep(0.2)
                self.fill_processes()
            except Exception as e:
                QMessageBox.information(
                    self,
                    'Error',
                    'Cannot End Process.'
                )
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
                time.sleep(0.2)
                self.fill_processes()

            except Exception as e:
                QMessageBox.information(
                    self,
                    'Error',
                    'Cannot End Process.'
                    )
        else:
           QMessageBox.information(
               self,
               'Error ',
               'No Process Selected.'
           )
    
    def createplot(self,title,range,color):
        plot = pg.PlotWidget(title=title)
        plot.showGrid(x=True, y=True, alpha = 0.3)
        plot.setYRange(*range)
        plot.getPlotItem().getAxis('left').setPen('k')
        plot.getPlotItem().getAxis('bottom').setPen('k')
        plot.plot(pen=pg.mkPen(color,width = 2))
        return plot
    
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())