import sys
import threading
import time
import exceptions
from core.Observer import Observer
from core.SessionStatus import SessionStatus
from common.UpdateStatisticsWorker import *
from time import sleep,ctime

PROTOCOL = 0
ID = 1
ADDR = 2
TIME = 3
STATUS = 4
DESTINATION = 5
CLIENT_PORT = 6

HEAD = ['PROTOCOL','ID','ADDR','TIME','STATUS','DESTINATION','CLIENT_PORT']

WIDTH = {
    "PROTOCOL"        :        10,
    "ID"              :        4,
    "ADDR"            :        40,
    "TIME"            :        4,
    "STATUS"          :        14,
    "DESTINATION"     :        16,
    "CLIENT_PORT"     :        12
        }

INFO = ["TOTAL","INIT","START","PLAY","PAUSE","STOP"]

ansi = {
    'black': '\033[0;30m',
    'darkred': '\033[0;31m',
    'darkgreen': '\033[0;32m',
    'darkyellow': '\033[0;33m',
    'darkblue': '\033[0;34m',
    'darkmagenta': '\033[0;35m',
    'darkcyan': '\033[0;36m',
    'silver': '\033[0;37m',

    'gray': '\033[1;30m',
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[1;34m',
    'magenta': '\033[1;35m',
    'cyan': '\033[1;36m',
    'white': '\033[1;37m',

    'blackbg': '\033[40m',
    'redbg': '\033[41m',
    'greenbg': '\033[42m',
    'yellowbg': '\033[43m',
    'bluebg': '\033[44m',
    'magentabg': '\033[45m',
    'cyanbg': '\033[46m',
    'whitebg': '\033[47m',

    'reset': '\033[0;0m',
    'bold': '\033[1m',
    'reverse': '\033[2m',
    'underline': '\033[4m',

    'clear': '\033[2J',
    'clearline': '\033[K',
    'clearline': '\033[2K',
    'save': '\033[s',
    'restore': '\033[u',
    'save': '\0337',
    'restore': '\0338',

    'up': '\033[1A',
    'down': '\033[1B',
    'right': '\033[1C',
    'left': '\033[1D',

    'default': '\033[0;0m',
}

char = {
    'pipe':'|',
    'colon':':',
    'gt':'>',
    'space':' ',
    'dash':'-',
}

class ui_term(Observer,UpdateInterface):
    def __init__(self,manager = None):    
        self.statusMap = {
            SessionStatus.RUNNING:"Running",
            SessionStatus.STOPPED:'Stopped',
            SessionStatus.INITIAL:'Initial',
            SessionStatus.CONNECTING:'Connecting',
            SessionStatus.NETWORKERROR:'Failed',
            SessionStatus.EXECPTION:'Exception',
            SessionStatus.REMOVED:'Remove',
            SessionStatus.PAUSE:'Pause',
            SessionStatus.SETUP:'Setup',
        }
        self.session_records = []
        self.statics = None
        self.manager = manager
        self.accelerate = {}
        self.updateWorker = UpdateStatisticsWorker(self,manager)
        self.lock = threading.Lock()
        self.info = ""
        self.count = 0

    def __format(self,array):
        array[0] = ansi['darkblue'] + str(array[0]) + " " * (WIDTH["PROTOCOL"] - len(str(array[0]))) + ansi['default'] 
        array[1] = ansi['darkyellow'] + str(array[1]) + " " * (WIDTH["ID"] - len(str(array[1]))) + ansi['default']
        array[2] = ansi['white'] + str(array[2]) + " " * (WIDTH["ADDR"] - len(str(array[2]))) + ansi['default'] 
        array[3] = ansi['darkgreen'] + str(array[3]) + " " * (WIDTH["TIME"] - len(str(array[3]))) + ansi['default']
        if array[4].find("Failed") == -1:
            array[4] = ansi['darkgreen'] + str(array[4]) + " " * (WIDTH["STATUS"] - len(str(array[4]))) + ansi['default']
        else:
            array[4] = ansi['darkred'] + str(array[4]) + " " * (WIDTH["STATUS"] - len(str(array[4]))) + ansi['default']
        array[5] = ansi['default'] + str(array[5]) + " " * (WIDTH["DESTINATION"] - len(str(array[5])))
        array[6] = ansi['darkyellow'] + str(array[6]) + " " * (WIDTH["CLIENT_PORT"] - len(str(array[6]))) + ansi['default']
        arraystr = ""
        for each in array:
            arraystr += str(each)
        return arraystr

    def restore_scrn(self):
        sys.stdout.write(ansi['default'])

    def display_head(self):
        string = self.__format(HEAD)        
        sys.stdout.write(string + '\n')

    def display_info(self):
        sys.stdout.write(ansi['white'] + self.info + '\n')
        
    def display_line(self,array):
        string = self.__format(array)    
        sys.stdout.write(string + '\n')

    def __del__(self):
        self.manager.stop()
    
    def createView(self):     
        self.display_head()
        self.updateWorker.start()

    def update(self,statics):
        total   = statics.total()
        setup   = statics[SessionStatus.SETUP]
        run     = statics[SessionStatus.RUNNING] 
        stop    = statics[SessionStatus.STOPPED]
        fail    = statics[SessionStatus.NETWORKERROR]
        connect = statics[SessionStatus.CONNECTING]
        paused  = statics[SessionStatus.PAUSE]
        initial = statics[SessionStatus.INITIAL]

        
        self.info = str("\nTotal = %d   Initial = %d   Connect = %d   Setup = %d   Run = %d   Paused = %d   Failed = %d   Stop = %d\n" 
                        % (total, initial, connect, setup, run, paused, fail, stop))

    def addNewSession(self,status):
        protocol = status.getProtocol()
        id = status.getId()
        sessionStatus = self.statusMap[status.getStatus()]
        runTime = status.getTime()
        address = status.getAddress()
        params = status.getParamsFromRemote()
        destination = "NoAddress"
        port = "NoPort"
        session_record = [protocol,id,address,runTime,sessionStatus,destination,port]
        self.accelerate[id] = session_record
        self.session_records.append(session_record)
        self.display_line(session_record)

    def __clearStoppedSession(self,id):
        del self.accelerate[id]
        self.session_records.remove[id]

    def updateSessionStatus(self,status):
        self.lock.acquire()
        if status.getId() in self.accelerate.keys():
            id = status.getId()
            self.accelerate[id][STATUS] = self.statusMap[status.getStatus()]
            self.accelerate[id][TIME] = status.getTime()
            if self.accelerate[id][STATUS] == "Setup":
                self.accelerate[id][DESTINATION] = status.getParamsFromRemote()['destination']
                self.accelerate[id][CLIENT_PORT] = status.getParamsFromRemote()['client_port']
            self.count += 1
            if self.count > len(self.accelerate.keys()):
                for each in self.session_records:
                    self.display_line(each)
                self.display_info()
                time.sleep(1.5)
                self.count = 0
        else:
            self.addNewSession(status)
        self.lock.release()  

    def updateView(self,status):
        self.updateSessionStatus(status)

if __name__ == '__main__':    
    pass
