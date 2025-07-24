import psutil
from Tasks import Tasks
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
            
