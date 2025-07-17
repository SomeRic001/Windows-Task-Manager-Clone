import psutil
from Tasks import Tasks
import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QWidget,QLabel
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.total_proc=0
        self.totalmem_per = 0
        self.totalcpu = 0
    def processes(self):
        for proc in psutil.process_iter():
            pid = proc.pid
            name = proc.name()
            if name.lower() == "system idle process" :
                continue
            memory = round((proc.memory_info().rss)/(1024*1024),3)
            cpu = proc.cpu_percent(interval = 0.1)/psutil.cpu_count()
            process = Tasks(name,pid,memory,cpu)
            self.total_proc+=1
            self.totalmem_per += proc.memory_percent()
            self.totalcpu +=cpu
            self.tasks.append(process.stpr())
        
            
    def display(self):
        print(self.total_proc)
        print(self.totalmem_per)
        print(self.totalcpu)
        for i in self.tasks:
            print(i)
     
'''class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Manager")
        self.resize(480,720)
        widget = QLabel("Hello")
        font = widget.font()
        font.setPointSize(30)
        widget.setFont(font)
        widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.setCentralWidget(widget)
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())'''
T = TaskManager()
T.processes()
T.display()