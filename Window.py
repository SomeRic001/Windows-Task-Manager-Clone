from Taskmanager import TaskManager
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
import subprocess
import sys
import time
import psutil
from collections import defaultdict
class TaskTreeItem(QTreeWidgetItem):
    def __lt__(self,other):
        column = self.treeWidget().sortColumn()
        if self.parent() is None and other.parent() is None:
            try:
                return float(self.text(column))<float(other.text(column))
            except (ValueError,TypeError):
                return self.text(column).lower()< other.text(column).lower()
        return False
        
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
        self.pid_column_index = 3
        header = self.tree.header()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        self.tree.setSortingEnabled(True)
        self.tree.sortItems(0,Qt.AscendingOrder)
        self.tree.setColumnWidth(0,300)
        self.fill_processes()
        self.tree.itemClicked.connect(self.get_pid)
        self.main_layout.addWidget(self.tree,stretch=4)
        #Process Timer for Updating Process
        self.process_timer.timeout.connect(self.fill_processes)
        self.process_timer.start(10000)
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
        pg.setConfigOption('background',"#f2f2f2c5")
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

        scroll_pos = self.tree.verticalScrollBar().value()
        self.tree.setColumnCount(4)

        
        headerlabels = ["Process", "Memory(MB)", "CPU(%)", "PID"]
        self.tree.setHeaderLabels(headerlabels)

        root = self.tree.invisibleRootItem()
        while root.childCount() > 0:
            root.removeChild(root.child(0))
    # Grouping tasks with same name
        grouped = defaultdict(list)
        for task in self.T.tasks:
            grouped[task['Process']].append(task)

        for name, group in grouped.items():
            count = len(group)
            total_cpu = sum(float(p.get("CPU(%)", 0)) for p in group)
            total_mem = sum(float(p.get("Memory(MB)", 0)) for p in group)

            parent = TaskTreeItem(self.tree)
            parent.setText(0, f"{name} ({count} instances)")
            parent.setText(1, f"{total_mem:.2f}")
            parent.setText(2, f"{total_cpu:.2f}")
            parent.setExpanded(False)

            for task in group:
                child = QTreeWidgetItem()
                child.setText(0, task.get("Process", ""))
                child.setText(1, str(task.get("Memory(MB)", "")))
                child.setText(2, str(task.get("CPU(%)", "")))
                child.setText(3, str(task.get("PID","")))
                parent.addChild(child)

        self.tree.verticalScrollBar().setValue(scroll_pos)
            
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
        if not p_id.isdigit():
            child_pids = []
            for i in range(item.childCount()):
                child = item.child(i)
                pid_text = child.text(self.pid_column_index)
                if pid_text.isdigit():
                    child_pids.append(int(pid_text))
            if child_pids:
                self.ids = child_pids
            else:
                self.ids = None
            return
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
        if getattr(self,'id',None) is not None:
            try:
                proc = psutil.Process(self.id)
                proc.terminate()
                time.sleep(0.2)
                self.fill_processes()
                self.id = None
            except Exception as e:
                print (e)
                QMessageBox.information(
                    self,
                    'Error',
                    'Cannot End Process.'
                )
        elif getattr(self, 'ids',None):
            failed = False
            for id in self.ids:
                try:
                    proc = psutil.Process(id)
                    proc.terminate()
               
                except Exception as e:
                    failed = True
            time.sleep(0.2)
            self.fill_processes()
            self.ids = None
            if failed:
                    QMessageBox.information(
                        self,
                        'Error ',
                        'Cannot End Process.'
                         )
        else:
            QMessageBox.information(
                self,
                'Error ',
                'No process Selected.'
                )

    def force_kill(self):
        if getattr(self,'id',None) is not None:
            try:
                proc = psutil.Process(self.id)
                proc.kill()
                time.sleep(0.2)
                self.fill_processes()
                self.id = None
            except Exception as e:
                print (e)
                QMessageBox.information(
                    self,
                    'Error',
                    'Cannot End Process.'
                )
        elif getattr(self, 'ids',None):
            failed = False
            for id in self.ids:
                try:
                    proc = psutil.Process(id)
                    proc.kill()
               
                except Exception as e:
                    failed = True
            time.sleep(0.2)
            self.fill_processes()
            self.ids = None
            if failed:
                    QMessageBox.information(
                        self,
                        'Error ',
                        'Cannot End Process.'
                         )
        else:
            QMessageBox.information(
                self,
                'Error ',
                'No process Selected.'
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