import base64, httplib, urllib2
from threading import Timer
import time
httplib.HTTPConnection.debuglevel = 1

class Rovio:
    "Rovio class";
    data = {'prot':'http','realm':'Rovio', 'port':'80'};
    
    waiting = True;
    numrequests = 0;
    commands = {'Stop':'0',
             'Forward':'1',
             'Backward':'2',
             'Left':'3',
             'Right':'4',
             'TurnLeft':'5',
             'TurnRight':'6',
             'DFLeft':'7',
             'DFRight':'8',
             'DBLeft':'9',
             'DBRight':'10',
             'HeadUp':'11',
             'HeadDown':'12',
             'HeadMiddle':'13',
             'RotLeft20':'17',
             'RotRight20':'18'};   

    name = '';
    
    def __init__(self, host, name, uname=None, pword=None, port=80):
        self.data['host'] = host;
        self.data['user'] = uname;
        self.data['pass'] = pword;
        self.data['port'] = port
        self.name = name;
        self.sensors = RovioSensor(self);
        print 'Initialized rovio with name: ' + name + " and IP: " + self.data['host'];

    def stop(self):
        self.move('Stop');

    def headUp(self):
        self.move('HeadUp');
    def headDown(self):
        self.move('HeadDown');
    def headMiddle(self):
        self.move('HeadMiddle');
        

        
    def turnCW(self, degrees='90', speed='3'):
        self.turn('clockwise', degrees, speed);
        
    def turnCCW(self, degrees='90', speed='3'):
        self.turn('counter', degrees, speed);
    
    def turn(self, dir='clockwise',degrees='90',speed='3'):
#        print "TURNING";
        turnDir = '17';
        if(dir == 'clockwise'):
            turnDir = '18';

        url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=18' % self.data
        url = url + '&drive=' + turnDir +'&angle=' + str(int(degrees)/10) + '&speed=' + str(speed);

#        print url;
        req = urllib2.Request(url)

        if self.data['user'] is not None:
            base64string = base64.encodestring('%s:%s' % (self.data['user'], self.data['pass']))[:-1]
            req.add_header("Authorization", "Basic %s" % base64string)
    
        f = urllib2.urlopen(req)
        data = f.read()
#        print data    


    def move(self, direction, times=1):
#        print "Moving " + direction + " " + str(times) + " units";
        for i in range(0,times):
            self.navigate(self.commands[direction]);
            self.navigate(self.commands[direction]);    
            self.navigate(self.commands[direction]);
        
    def backward(self, times=1):
        self.move('Backward',times);

    def forward(self, times=1):
        self.move('Forward', times);

    def forward3(self):
        print "FORWARD3";
        self.move('Forward', 3);
#        self.wait(.015);
        
    # simple "wander" program. bangs into chair legs
    def wander(self):  
        for i in range(0,50):
            if(not self.sensors.obstacle()):
                self.forward3();
            else:
                self.turn();
                
        print "DONE WANDERING";

    def getReport(self):
        url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=1' % self.data
        print "Getting Report";

        print self.getRequestResponse(url); 


    def navigate(self, move):
        url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=18&drive=' % self.data
        url = url + move;

        self.getRequestResponse(url); 
       
    def getRequestResponse(self, url):
#        print "getRequestResponse with URL: " + url;
        
        self.numrequests = self.numrequests + 1;
#        print "Requests " + str(self.numrequests);
        
        req = urllib2.Request(url)
        if self.data['user'] is not None:
            base64string = base64.encodestring('%s:%s' % (self.data['user'], self.data['pass']))[:-1]
            req.add_header("Authorization", "Basic %s" % base64string)
    
        f = urllib2.urlopen(req)
        data = f.read()
        return data;       
    
    def wait(self, seconds):
        time.sleep(seconds);
        
    def getMCUReportValue(self):
        # get the MCU report
        report = str(self.getMCUReport());
        # get the string that encodes (in hex) the status
        status = report.split('\n')[1].split(' ')[2];
        # return it
        return status;

    def getMCUReport(self):
        print "getting MCUReport";

        url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=20' % self.data
        print "Getting Report";
        return self.getRequestResponse(url);

class RovioSensor:
    "Interface to Rovio sensor data, including webcam"
    def __init__(self, rovio):
        "rovio: the initialized Rovio controller to use"
        self.rovio = rovio

    def camImage(self):
        "Returns camera image"
        
    def obstacle(self):    
        "Returns True if there's an obstacle, False otherwise"
        # get just the status string from the MCU report
        status = self.rovio.getMCUReportValue();
        # get the last character, convert it to an integer
        lastByte = int("0x" + status[len(status)-1], 16);
        # the obstacle indicator is on bit 2
        # take bitwise & with 00000100 (4 in base 10)
        return ((lastByte & 4) > 0);
        

