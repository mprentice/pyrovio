import Rovio;
import sys
from threading import Timer;

def main(argv=None):
    if argv is None:
        argv = sys.argv
    # hostname, rovio name, username, password
    karl = Rovio.Rovio('192.168.0.40','karl', 'rovio1', 'rovio1');
#    karl = Rovio.Rovio('192.168.1.102','vanessa', 'mprentice', 'ecitnerp')

#    karl.getReport();

#    karl.wander();
    
    karl.forward();
    karl.wander();
    
    if (karl.sensors.obstacle()):
        print "OBSTACLE";
    else:
        print "NO OBSTACLE";

#    # turn 90degrees clockwise
#    karl.turnCW(90);
#    # heads up!
#    karl.headUp();
#    # move forward one unit ten times
#    karl.forward(10);
#    # wait 4 seconds - why not?
#    karl.wait(4);
#    # turn 90degrees ccwise
#    karl.turnCCW(90);
#    # heads down!
#    karl.headDown();
#    # return success
#    return 0

if __name__ == "__main__":
    sys.exit(main())
