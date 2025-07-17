import psutil
class Tasks:
    def __init__(self,name,pid,memory,cpu):
        self.pid = pid
        self.name = name
        self.memory = memory
        self.cpu = cpu
    def kill(self):
        try:
            process = psutil.Process(self.pid)
            process.terminate()
        except psutil.NoSuchProcess as e:
            print(f"ERROR!! Process not found. {e}")
            return -1
        except psutil.AccessDenied as d:
            print(f"Access Denied! {d}")
            return -2
        else:
            print("Terminated successfully.")
            return 1
    def stpr(self):
        return {'Process':self.name, 'Memory': self.memory , 'CPU': self.cpu }

