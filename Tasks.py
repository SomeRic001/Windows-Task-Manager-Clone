import psutil
class Tasks:
    def __init__(self,num,name,pid,memory,cpu):
        self.pid = pid
        self.name = name
        self.memory = memory
        self.cpu = cpu
        self.num = num
        
    def stpr(self):
        return { 'Process':self.name, 'Memory(MB)': self.memory , 'CPU(%)': self.cpu,'PID':self.pid }

