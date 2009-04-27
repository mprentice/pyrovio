"""
A Python implementation of the Wowwee Rovio web-based API.

The Rovio mobile webcam is controlled through a web-based API.  The Rovio class
wraps http calls to a Rovio and returns the appropriate responses.  It also
provides some additional support methods for parsing the responses.

Classes:
    Rovio: Access to an instance of a Rovio mobile webcam

Exceptions:
    RovioError: base class for Rovio-related exceptions

Module Constants:
    __version__: The version of the PyRovio interface module as a string
    API_VERSION: The version of the Rovio API as a string
    API_DATE: Release date of the Rovio API
    INFO: PyRovio version and API info as a string
    AUTHORS: List of dicts of author names and emails
    COPYRIGHT
    LICENSE
    USER_AGENT: For use with HTTP requests

    Response Code Commands Table

    These are returned by many Rovio commands.

    #  Constant name                    Description
    ---------------------------------------------------------------------------
    0  SUCCESS                          CGI command successful
    1  FAILURE                          CGI command general failure
    2  ROBOT_BUSY                       robot is executing autonomous function
    3  FEATURE_NOT_IMPLEMENTED          CGI command not implemented
    4  UNKNOWN_CGI_ACTION               CGI nav command: unknown action
                                        requested
    5  NO_NS_SIGNAL                     no navigation signal available
    6  NO_EMPTY_PATH_AVAILABLE          path memory is full
    7  FAILED_TO_READ_PATH              failed to read Flash memory
    8  PATH_BASEADDRESS_NOT_INITIALIZED Flash error
    9  PATH_NOT_FOUND                   no path with such name
    10 PATH_NAME_NOT_SPECIFIED          path name parameter is missing
    11 NOT_RECORDING_PATH               save path command received while not in
                                        recording mode
    12 FLASH_NOT_INITIALIZED            Flash subsystem failure
    13 FAILED_TO_DELETE_PATH            Flash operation failed
    14 FAILED_TO_READ_FROM_FLASH        Flash operation failed
    15 FAILED_TO_WRITE_TO_FLASH         Flash operation failed
    16 FLASH_NOT_READY                  Flash failed
    17 NO_MEMORY_AVAILABLE              N/A
    18 NO_MCU_PORT_AVAILABLE            N/A
    19 NO_NS_PORT_AVAILABLE             N/A
    20 NS_UART_READ_ERROR               N/A
    21 PARAMETER_OUTOFRANGE             one or more CGI parameters are out of
                                        expected range
    22 NO_PARAMETER                     one or more CGI parameters are missing

Authors:
  - Jon Bona (University at Buffalo) (mailto:jpbona@buffalo.edu)
  - Mike Prentice (University at Buffalo) (mailto:mjp44@buffalo.edu)

PyRovio is developed by the University at Buffalo and distributed under the UB
Public License (UBPL) version 1.0 (see license.txt).

"""

import base64, urllib2
from threading import Timer
import time

###############
# MODULE INFO #
###############

# Some third-party software expects __version__
__version__ = '0.1'
API_VERSION = '1.2'
API_DATE = 'October 8, 2008'
INFO = 'PyRovio v%s ; Rovio API v%s released %s' % (__version__, API_VERSION,
                                                    API_DATE)
AUTHORS = [{'name' : 'Mike Prentice', 'email' : 'mjp44@buffalo.edu'},
           {'name' : 'Jon Bona', 'email' : 'jpbona@buffalo.edu'}]
COPYRIGHT = 'Copyright (C) 2009 Jon Bona and Mike Prentice'
LICENSE = 'UBPL v1.0'

####################
# MODULE CONSTANTS #
####################

USER_AGENT = 'PyRovio/%s' % __version__

# Response Code Commands
SUCCESS                          = 0
FAILURE                          = 1
ROBOT_BUSY                       = 2
"""robot is executing autonomous function"""
FEATURE_NOT_IMPLEMENTED          = 3
UNKNOWN_CGI_ACTION               = 4
NO_NS_SIGNAL                     = 5
"""no navigation signal available"""
NO_EMPTY_PATH_AVAILABLE          = 6
"""path memory is full"""
FAILED_TO_READ_PATH              = 7
"""failed to read FLASH memory"""
PATH_BASEADDRESS_NOT_INITIALIZED = 8
"""FLASH error"""
PATH_NOT_FOUND                   = 9
"""no path with such name"""
PATH_NAME_NOT_SPECIFIED          = 10
"""path name parameter is missing"""
NOT_RECORDING_PATH               = 11
"""save path command received while not in recording mode"""
FLASH_NOT_INITIALIZED            = 12
"""FLASH subsystem failure"""
FAILED_TO_DELETE_PATH            = 13
"""FLASH operation failed"""
FAILED_TO_READ_FROM_FLASH        = 14
"""FLASH operation failed"""
FAILED_TO_WRITE_TO_FLASH         = 15
"""FLASH operation failed"""
FLASH_NOT_READY                  = 16
"""FLASH failed"""
NO_MEMORY_AVAILABLE              = 17
NO_MCU_PORT_AVAILABLE            = 18
NO_NS_PORT_AVAILABLE             = 19
NS_UART_READ_ERROR               = 21
PARAMETER_OUTOFRANGE             = 22
"""one or more CGI parameters are out of expected range"""
NO_PARAMETER                     = 23
"""one or more CGI parameters are missing"""

response_codes = {
    SUCCESS : ['SUCCESS', 'CGI command successful'],
    FAILURE : ['FAILURE', 'CGI command general failure'],
    ROBOT_BUSY : ['ROBOT_BUSY', 'robot is executing autonomous function'],
    FEATURE_NOT_IMPLEMENTED : ['FEATURE_NOT_IMPLEMENTED',
                               'CGI command not implemented'],
    UNKNOWN_CGI_ACTION : ['UNKNOWN_CGI_ACTION',
                          'CGI nav command: unknown action requested'],
    NO_NS_SIGNAL : ['NO_NS_SIGNAL', 'no navigation signal available'],
    NO_EMPTY_PATH_AVAILABLE : ['NO_EMPTY_PATH_AVAILABLE',
                               'path memory is full'],
    FAILED_TO_READ_PATH : ['FAILED_TO_READ_PATH',
                           'failed to read Flash memory'],
    PATH_BASEADDRESS_NOT_INITIALIZED : ['PATH_BASEADDRESS_NOT_INITIALIZED',
                                        'Flash error'],
    PATH_NOT_FOUND : ['PATH_NOT_FOUND', 'no path with such name'],
    PATH_NAME_NOT_SPECIFIED : ['PATH_NAME_NOT_SPECIFIED',
                               'path name parameter is missing'],
    NOT_RECORDING_PATH : ['NOT_RECORDING_PATH',
                          'save path command received while not in recording '
                          'mode'],
    FLASH_NOT_INITIALIZED : ['FLASH_NOT_INITIALIZED',
                             'Flash subsystem failure'],
    FAILED_TO_DELETE_PATH : ['FAILED_TO_DELETE_PATH',
                             'Flash operation failed'],
    FAILED_TO_READ_FROM_FLASH : ['FAILED_TO_READ_FROM_FLASH',
                                 'Flash operation failed'],
    FAILED_TO_WRITE_TO_FLASH : ['FAILED_TO_WRITE_TO_FLASH',
                                'Flash operation failed'],
    FLASH_NOT_READY : ['FLASH_NOT_READY', 'Flash failed'],
    NO_MEMORY_AVAILABLE : ['NO_MEMORY_AVAILABLE', 'N/A'],
    NO_MCU_PORT_AVAILABLE : ['NO_MCU_PORT_AVAILABLE', 'N/A'],
    NO_NS_PORT_AVAILABLE : ['NO_NS_PORT_AVAILABLE', 'N/A'],
    NS_UART_READ_ERROR : ['NS_UART_READ_ERROR', 'N/A'],
    PARAMETER_OUTOFRANGE : ['PARAMETER_OUTOFRANGE',
                            'one or more CGI parameters are out of expected '
                            'range'],
    NO_PARAMETER : ['NO_PARAMETER', 'one or more CGI parameters are missing'],
    }

###########
# CLASSES #
###########

class RovioError(Exception):
    """Base class for errors in the Rovio package."""

class ConnectError(RovioError):
    """
    Exception raised for error connecting to the Rovio.

    Attributes:
      - rovio: Rovio object
      - message: explanation of the error

    """

    def __init__(self, rovio):
        self.rovio = rovio
        self.message = ('Error connecting to %s (host: %s)' %
                        (self.rovio.name, self.rovio.host))

class ResponseError(RovioError):
    """
    Exception raised for a command response code error.

    Raised when the response code is not SUCCESS.

    Attributes:
      - rovio: Rovio object
      - code: command response code
      - message: explanation of the error

    """

    def __init__(self, rovio, code):
        self.rovio = rovio
        self.code = code
        self.message = ('\n'.join(['Response error from %s',
                                   '    Command response code: %d %s',
                                   '    %s']) %
                        (self.code,
                         response_codes[self.code][0],
                         response_codes[self.code][1]))

class Rovio:
    
    """
    An instance of the Rovio class provides an interface to one Rovio.

    The Rovio API consists of function calls made over HTTP.  This class wraps
    the HTTP requests with Python method calls.  The Rovio API is mirrored as
    faithfully as possible; however, some convenience functions have been used.
    For example, the movement commands are implemented as separate methods
    rather than parameters to the ManualDrive method in the Rovio API.

    You can set the hostname of the Rovio to connect to using the host
    property.  You can also set the IP address or host of the Rovio webcam
    itself using the Rovio API using SetHTTP.  After using SetHTTP, you are
    required to then set the host property to the same address in order to
    continue controlling the same Rovio object.  (Note: This was an arbitrary
    design decision in making the Rovio class.)  TODO: example

    WARNING: There is not much parameter checking.  The only indicator that
    things aren't working may be that the object is not able to connect to the
    Rovio's webserver, so set parameters carefully.

    Properties:
      - name:     name of this Rovio (read-only)
      - host:     hostname or IP address of the Rovio
      - protocol: Protocol to use (read-only, default http)
      - port:     HTTP port number (default 80)
      - speed:    Default Rovio speed (1 fastest, 10 slowest, default 1)
      - username: HTTP Auth name (default None)
      - password: HTTP Auth password (default None)

    Commands:
      - GetReport: returns a status report on the Rovio
      - StartRecording: start recording a path

    Movement commands:
    
    All movement commands return a response code (SUCCESS for success, see
    Response Code Commands Table).  Non-camera movement commands have an
    optional speed parameter that defaults to the default speed of this Rovio
    object.
    
      - Stop
      - Forward
      - Backward
      - Left (straight left)
      - Right (straight right)
      - RotateLeft (by speed)
      - RotateRight (by speed)
      - DiagForwardLeft
      - DiagForwardRight
      - DiagBackLeft
      - DiagBackRight
      - HeadUp (camera)
      - HeadDown (camera)
      - HeadMiddle (camera)
      - RotateLeft20 (20 degrees)
      - RotateRight20 (20 degrees)

    Helper commands:
    
    These commands should not be called directly, but are available if
    necessary.
    
      - getRequestResponse: execute the Rovio command and return raw response
      - ManualDrive: master command for wheel and camera movement

    Documentation taken from the API Specification for Rovio, version 1.2,
    October 8, 2008, from WowWee Group Limited.
    
    """
    
    # Class constants

    # Data attributes (instance attributes)
    
    def getProtocol(self): return self._protocol
    protocol = property(getProtocol, doc="""Protocol to use (default http)""")
    
    def getPort(self): return self._port
    def setPort(self, value):
        # TODO: Throw exception on bad value
        if (isinstance(value, int) and value > 0):
            self._port = value
            self._compileURLs()
    port = property(getPort, setPort,
                    doc="""Rovio port (default 80)""")

    def getSpeed(self): return self._speed
    def setSpeed(self, value):
        # TODO: Throw exception on bad value
        if (value >= 1 and value <= 10):
            self._speed = value
    speed = property(getSpeed, setSpeed,
                     doc="""
                     Rovio's default movement speed.

                     1 fastest, 10 slowest (default 1)
                     
                     """)

    def getUsername(self): return self._username
    def setUsername(self, value):
        # TODO: Throw exception on bad value
        if (isinstance(value, str) or value is None):
            self._username = value
            self._compileURLs()
    username = property(getUsername, setUsername,
                        doc="""HTTP Auth username or None""")

    def getPassword(self): return self._password
    def setPassword(self, value):
        # TODO: Throw exception on bad value
        if (isinstance(value, str) or value is None):
            self._password = value
            self._compileURLs()
    password = property(getPassword, setPassword,
                        doc="""HTTP Auth password or None""")
    
    def getName(self): return self._name
    name = property(getName, doc="""Name of the Rovio the object represents""")

    def getHost(self): return self._host
    def setHost(self, value):
        # TODO: Throw exception on bad value
        if (isinstance(value, str)):
            self._host = value
            self._compileURLs()
    host = property(getHost, setHost,
                    doc="""Hostname or IP address of the Rovio""")
    
    def __init__(self, name, host, username=None, password=None, port=80):
        """
        Initialize a new Rovio interface.

        Parameters:
          - name:     name of this Rovio mobile webcam
          - host:     hostname or IP address
          - username: HTTP Auth name (default None)
          - password: HTTP Auth password (default None)
          - port:     HTTP port (default 80)

        """
        self._name = name
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._protocol = 'http'
        self._speed = 1
        self._compileURLs()

    def getRequestResponse(self, page):
        """
        Send a command to the Rovio and return its response.

        In general, this command should not be called directly.

        Parameters:
          - page: the Rovio API command to request

        Return the raw response.

        """
        url = self._base_url + page
        req = urllib2.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        if self._base64string is not None:
            req.add_header("Authorization", "Basic %s" % self._base64string)
        f = urllib2.urlopen(req)
        data = f.read()
        return data;

    def ManualDrive(self, command, speed=None):
        """
        Send a ManualDrive command to the Rovio.

        In general, this command should not be called directly.

        Parameters:
          - command: the movement command ID (integer)
                     0   stop
                     1   forward
                     2   backward
                     3   straight left
                     4   straight right
                     5   rotate left by speed
                     6   rotate right by speed
                     7   diagonal forward left
                     8   diagonal forward right
                     9   diagonal back left
                     10  diagonal back right
                     11  head up (camera)
                     12  head down (camera)
                     13  head middle (camera)
                     17  rotate left 20 degrees
                     18  rotate right 20 degrees
          - speed: speed to move (default is self.speed)

        Return the response code (0 for success).

        """
        if speed is None or speed < 1 or speed > 10:
            speed = self.speed
        page = ('rev.cgi?Cmd=nav&action=%d&drive=%d&speed=%d' %
                (18, command, speed))
        r = self.getRequestResponse(page)
        return self._parseResponse(r)['responses']

    def Stop(self):
        """Currently does nothing."""
        return self.ManualDrive(0)

    def Forward(self, speed=None):
        """Move Rovio forward."""
        return self.ManualDrive(1, speed)

    def Backward(self, speed=None):
        """Move Rovio backward."""
        return self.ManualDrive(2, speed)

    def Left(self, speed=None):
        """Move Rovio straight left."""
        return self.ManualDrive(3, speed)

    def Right(self, speed=None):
        """Move Rovio straight right."""
        return self.ManualDrive(4, speed)

    def RotateLeft(self, speed=None):
        """Rotate Rovio left by speed."""
        return self.ManualDrive(5, speed)

    def RotateRight(self, speed=None):
        """Rotate Rovio right by speed."""
        return self.ManualDrive(6, speed)

    def DiagForwardLeft(self, speed=None):
        """Move Rovio forward and left."""
        return self.ManualDrive(7, speed)

    def DiagForwardRight(self, speed=None):
        """Move Rovio forward and right."""
        return self.ManualDrive(8, speed)

    def DiagBackLeft(self, speed=None):
        """Move Rovio backward and left."""
        return self.ManualDrive(9, speed)

    def DiagBackRight(self, speed=None):
        """Move Rovio backward and right."""
        return self.ManualDrive(10, speed)

    def RotateLeft20(self):
        """Rotate Rovio left 20 degrees."""
        return self.ManualDrive(17)

    def RotateRight20(self):
        """Rotate Rovio right 20 degrees."""
        return self.ManualDrive(18)

    def HeadUp(self):
        """Camera head looking up."""
        return self.ManualDrive(11)

    def HeadDown(self):
        """Camera head down, looking ahead."""
        return self.ManualDrive(12)

    def HeadMiddle(self):
        """Camera head in middle position, looking ahead."""
        return self.ManualDrive(13)

    def GetReport(self):
        """
        Get Rovio's current status.

        Generates a report from libNS module that provides Rovio's current
        status.  Return a dictionary (keys are strings).

        Key                Description
        -----------------------------------------------------------------------
        responses          error checking (0: no error)
        x, y, theta        average location of Rovio in relation to the
                           strongest room beacon
                           x,y: -32767--32768
                           theta: -PI--PI
        room               room ID (0: home base, 1--9: mutable room projector)
        ss                 navigation signal strength
                           0--65535 (16 bit)
                           Strong signal > 47000
                           No signal < 5000
        beacon             signal strength for docking beacon when available
                           0--65535 (16 bit)
        beacon_x           horizontal position of beacon as seen by navigation
                           system (-32767--32768)
        next_room          the next strongest room beacon ID seen
                           -1: no room found
                           1--9: mutable room ID
        next_room_ss       the signal strength of the next strongest room
                           beacon
                           0--65535 (16 bit)
                           Strong signal > 47000
                           No signal < 5000
        state              0: idle
                           1: driving home
                           2: docking
                           3: executing path
                           4: recording path
        resistance         status of robot resistant to drive into navigation
                           system-deprived areas (NOT IN USE)
        sm                 currect status of the navigation state machine (for
                           debugging purposes)
        pp                 current way point when using path (1--10)
        flags              1: home position
                           2: obstacle detected
                           3: IR detector activated
        brightness         the current brightness (1 dimmest, 6 brightest)
        raw_resolution     0: [176x144]
                           1: [320x240]
                           2: [352x240]
                           3: [640x480]
        resolution         size of camera image as a list of [horz, vert]
        video_compression  0: low, 1: medium, 2: high
        frame_rate         video frame rate (1--30 fps)
        privilege          show current user privilege status
                           0: administrator
                           1: guest user
        user_check         whether need login and password (0 no, 1 yes)
        speaker_volume     0 (lowest) -- 31 (highest)
        mic_volume         0 (lowest) -- 31 (highest)
        wifi_ss            Wifi signal strength (0--254)
        show_time          whether to show time in the image (0 no, 1 yes)
        ddns_state         DDNS update status
                           0: no update
                           1: updating
                           2: update successful
                           3: update failed
        email_state        current status of email client (NOT IN USE)
        battery            < 100: turn self off
                           100--106: try to go home
                           106--127: normal
        charging           0--79: not charging
                           80: charging
        raw_head_position  204: position low
                           135--140: position mid-way
                           65: position high
        head_position      'low', 'mid', or 'high'
        raw_ac_freq        projector's frequency
                           0: not detected
                           1: 50 Hz
                           2: 60 Hz
        ac_freq            projector's frequency in Hz, or 0 if none

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (1,)
        r = self.getRequestResponse(page)
        d = self._parseResponse(r)
        # TODO: flags?
        d['raw_resolution'] = d['resolution']
        if d['raw_resolution'] == 0:
            d['resolution'] = [176,144]
        elif d['raw_resolution'] == 1:
            d['resolution'] = [320,240]
        elif d['raw_resolution'] == 2:
            d['resolution'] = [352,240]
        elif d['raw_resolution'] == 3:
            d['resolution'] = [640,480]
        d['raw_head_position'] = d['head_position']
        if d['raw_head_position'] < 135:
            d['head_position'] = 'high'
        elif d['raw_head_position'] > 140:
            d['head_position'] = 'low'
        else:
            d['head_position'] = 'mid'
        d['raw_ac_freq'] = d['ac_freq']
        if d['raw_ac_freq'] == 1:
            d['ac_freq'] = 50
        elif d['raw_ac_freq'] == 2:
            d['ac_freq'] = 60
        return d

    def StartRecording(self):
        """
        Start recording a path.

        Rovio will resist going outside NorthStar (navigation system) coverage
        area while recording path.

        Rovio will stop recording if coverage is lost.

        Rovio will stop recording if user connection is lost.

        Return a command response code.

        """
        return self._simpleRevCmd(2)

    def AbortRecording(self):
        """
        Terminate recording of path.

        Does not store to flash memory.

        Return a command response code.

        """
        return self._simpleRevCmd(3)

    def StopRecording(self, path_name='newpath'):
        """
        Stop recording and save path to flash memory.

        Path name should contain only alphanumeric characters (no whitespace or
        punctuation).

        Parameters:
          - path_name: name for saving path (default 'newpath')

        Return a command response code.

        """
        return self._simpleRevCmd(4, path_name)

    def DeletePath(self, path_name):
        """
        Delete the specified path.

        Parameters:
          - path_name: the path to delete

        Return a command response code.

        """
        return self._simpleRevCmd(5, path_name)

    ### TODO Continue testing here!

    def GetPathList(self):
        """Return a list of paths stored in the Rovio."""
        page = 'rev.cgi?Cmd=nav&action=%d' % (6,)
        return self.getRequestResponse(page)

    def PlayPathForward(self, path_name):
        """
        Replays a stored path from closest point to the end.

        If navigation signal is lost, it stops.

        Parameters:
          - path_name: name of path to play

        Return a command response code.

        """
        return self._simpleRevCmd(7, path_name)
        
    def PlayPathBackward(self, path_name):
        """
        Replays a stored path from closest point to the beginning.

        If navigation signal is lost, it stops.

        Parameters:
          - path_name: name of path to play

        Return a command response code.

        """
        return self._simpleRevCmd(8, path_name)

    def StopPlaying(self):
        """Stop playing a path."""
        return self._simpleRevCmd(9)

    def PausePlaying(self):
        """Pause the robot and wait for a new pause or stop command."""
        return self._simpleRevCmd(10)

    def RenamePath(self, old_path_name, new_path_name):
        """
        Rename the old path.

        Parameters:
          - old_path_name: old name of the path
          - new_path_name: new name of the path

        Return a command response code.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&name=%s&newname=%s' %
                (11, old_path_name, new_path_name))
        r = self.getRequestResponse(page)
        return self._parseResponse(r)['responses']

    def GoHome(self):
        """Drive to home location in front of charging station."""
        return self._simpleRevCmd(12)

    def GoHomeAndDock(self):
        """Drive to home location and dock at charging station."""
        return self._simpleRevCmd(13)

    def UpdateHomePosition(self):
        """Define current position as home location."""
        return self._simpleRevCmd(14)

    def SetTuningParameters(self):
        """
        Change homing, docking, and driving parameters.

        Speed for driving commands.

        Return a command response code.

        """
        return self._simpleRevCmd(15)

    def GetTuningParameters(self):
        """Return home, docking, and driving parameters."""
        page = 'rev.cgi?Cmd=nav&action=%d' % (16,)
        r = self.getRequestResponse(page)
        return self._parseResponse(r)

    def ResetNavStateMachine(self):
        """Stops whatever it was doing and resets to idle state."""
        return self._simpleRevCmd(17)

    def GetMCUReport(self):
        """
        Returns MCU report (motor controller unit?).

        Including wheel encoders and IR obstacle avoidance.

        Return a byte sequence.

        Offset Length Description
        -----------------------------------------------------------------------
        0      1B     Length of the packet
        1      1B     NOT IN USE
        2      1B     Direction of rotation of left wheel since last read
                      (bit 2)
        3      2B     Number of left wheel encoder ticks since last read
        5      1B     Direction of rotation of right wheel since last read
                      (bit 2)
        6      2B     Number of right wheel encoder ticks since last read
        8      1B     Direction of rotation of rear wheel since last read
                      (bit 2)
        9      2B     Number of rear wheel encoder ticks since last read
        11     1B     NOT IN USE
        12     1B     Head position
        13     1B     0x7F: battery full (0x7f or higher for new battery)
                      0x??: orange light in Rovio head (to be defined)
                      0x6A: very low battery (hungry, danger, very low battery
                            level), libNS needs to take control to go home and
                            charge
                      0x64: shutdown level (MCU will cut off power for
                            protecting the battery)
        14     1B     bit 0: light LED (head) status, 0 off, 1 on
                      bit 1: IR-Radar power status, 0 off, 1 on
                      bit 2: IR-Radar detector status
                             0: fine
                             1: barrier detected
                      bit 3--5: charger status
                                0x00: nothing happening
                                0x01: charging completed
                                0x02: in charging
                                0x04: something wrong, error occurred
                      bit 6,7: undefined, not used

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (20,)
        return self.getRequestResponse(page)

    def ClearAllPaths(self):
        """Delete all paths in flash memory."""
        return self._simpleRevCmd(21)

    def GetStatus(self):
        """
        Report navigation state.

        Return a dictionary:
        {'responses': response code,
         'state': 0 (idle)
                  1 (driving home)
                  2 (docking)
                  3 (executing path)
                  4 (recording path)}

        """
        page = 'rev.cgi?Cmd=nav&action=%d' % (22,)
        r = self.getRequestResponse(page)
        return self._parseResponse(r)

    def SaveParameter(self, index, value):
        """
        Stores parameter in the robot's flash.

        Parameters:
          - index: 0--19
          - value: 32-bit signed integer

        Return response code NO_MEMORY_AVAILABLE or
        PARAMETER_OUTOFRANGE on error.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&index=%d&value=%d' %
                (23, index, value))
        r = self.getRequestResponse(page)
        return self._parseResponse(r)

    def ReadParameter(self, index):
        """
        Read parameter from the robot's flash.

        Parameters:
          - index: 0--19

        Return response code.

        """
        page = ('rev.cgi?Cmd=nav&action=%d&index=%d' % (24,
                                                        index))
        r = self.getRequestResponse(page)
        return self._parseResponse(r)

    def GetLibNSVersion(self):
        """Return string version of libNS and NS sensor."""
        return self._simpleRevCmd(25)

    def EmailImage(self, email):
        """
        Emails current image or if in path recording mode sets an action.

        Parameters:
          - email: email address

        """
        page = ('rev.cgi?Cmd=nav&action=%d&email=%d' % (26,
                                                        email))
        r = self.getRequestResponse(page)
        return self._parseResponse(r)

    def ResetHomeLocation(self):
        """Clear home location in flash memory."""
        return self._simpleRevCmd(27)

    def GetData(self):
        """
        Do nothing.
        
        Rovio API documentation on this command is not very good.  Does nothing
        at the moment.

        """
        return None

    def GetImage(self, imgID = None):
        """
        Acquire an image from the Rovio webcam.

        Parameters:
          - imgID: optional integer value for image tagging (default None)

        Return a JPEG image.

        """
        if imgID is None:
            return self.getRequestResponse('Jpeg/CamImg.jpg')
        else:
            return self.getRequestResponse('Jpeg/CamImg%d.jpg' % imgID)

    def StreamVideo(self):
        """Streaming video not yet supported."""
        return None

    def ChangeResolution(self, ResType=2, RedirectURL=None):
        """
        Change the resolution of the camera's images.

        Parameters:
          - ResType: Camera supports 4 resolutions.
                     0: 176x144
                     1: 352x288
                     2: 320x240 (default)
                     3: 640x480
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeResolution.cgi?ResType=%d' % (ResType,)
        else:
            page = ('ChangeResolution.cgi?ResType=%d&RedirectURL=%s' %
                    (ResType, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeCompressRatio(self, Ratio=1, RedirectURL=None):
        """
        Change the quality setting of camera's images (MPEG only).

        Parameters:
          - Ratio: 0 low, 1 medium, 2 high quality (default 1)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeCompressRatio.cgi?Ratio=%d' % (Ratio,)
        else:
            page = ('ChangeCompressRatio.cgi?Ratio=%d&RedirectURL=%s' %
                    (Ratio, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeFramerate(self, Framerate, RedirectURL=None):
        """
        Change the frame rate of camera's images.

        Parameters:
          - Framerate: 2--32 frames per second (default 30)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeFramerate.cgi?Framerate=%d' % (Framerate,)
        else:
            page = ('ChangeFramerate.cgi?Framerate=%d&RedirectURL=%s' %
                    (Framerate, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeFramerate(self, Framerate=30, RedirectURL=None):
        """
        Change the frame rate of camera's images.

        Parameters:
          - Framerate: 2--32 frames per second (default 30)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeFramerate.cgi?Framerate=%d' % (Framerate,)
        else:
            page = ('ChangeFramerate.cgi?Framerate=%d&RedirectURL=%s' %
                    (Framerate, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeBrightness(self, Brightness=6, RedirectURL=None):
        """
        Change the brightness of camera's images.

        Parameters:
          - Brightness: 0--6, lower is dimmer (default 6)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeBrightness.cgi?Brightness=%d' % (Brightness,)
        else:
            page = ('ChangeBrightness.cgi?Brightness=%d&RedirectURL=%s' %
                    (Brightness, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeSpeakerVolume(self, SpeakerVolume=15, RedirectURL=None):
        """
        Change the speaker volume of the Rovio.

        Parameters:
          - SpeakerVolume: 0--31, lower is quieter (default 15)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = ('ChangeSpeakerVolume.cgi?SpeakerVolume=%d' %
                    (SpeakerVolume,))
        else:
            page = ('ChangeSpeakerVolume.cgi?SpeakerVolume=%d&RedirectURL=%s' %
                    (SpeakerVolume, RedirectURL))
        return self.getRequestResponse(page)
        
    def ChangeMicVolume(self, MicVolume=15, RedirectURL=None):
        """
        Change the microphone volume of the Rovio.

        Parameters:
          - MicVolume: 0--31, lower is quieter (default 15)
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'ChangeMicVolume.cgi?MicVolume=%d' % (MicVolume,)
        else:
            page = ('ChangeMicVolume.cgi?MicVolume=%d&RedirectURL=%s' %
                    (MicVolume, RedirectURL))
        return self.getRequestResponse(page)
        
    def SetCamera(self, Frequency=0, RedirectURL=None):
        """
        Change camera sensor's settings.

        Parameters:
          - Frequency: 0: auto-detect (default), 50: 50Hz, 60: 60Hz
          - RedirectURL: undocumented (default None)

        Requires administrative privileges on the Rovio.
        
        """
        if RedirectURL is None:
            page = 'SetCamera.cgi?Frequency=%d' % (Frequency,)
        else:
            page = ('SetCamera.cgi?Frequency=%d&RedirectURL=%s' %
                    (Frequency, RedirectURL))
        return self.getRequestResponse(page)
        
    def _compileURLs(self):
        """Compile all URLs for use in getRequestResponse."""
        if self._username is not None and self._password is not None:
            self._base64string = base64.encodestring('%s:%s' %
                                                     (self._username,
                                                      self._password))[:-1]
        else:
            self._base64string = None
        self._base_url = '%s://%s:%d/' % (self._protocol, self._host,
                                          self._port)

    def _simpleRevCmd(self, commandID, name=None):
        """Make simple rev.cgi calls (for path ops, not ManualDrive)"""
        if name is None:
            page = 'rev.cgi?Cmd=nav&action=%d' % (commandID,)
        else:
            page = 'rev.cgi?Cmd=nav&action=%d&name=%s' % (commandID, name)
        r = self.getRequestResponse(page)
        return self._parseResponse(r)['responses']

    def _parseResponse(self, response):
        """
        Parse the response of some Rovio CGI commands.

        Responses are of the form (for example):
        'Cmd = nav\nresponses = 0\n|x=-5644|...'
        For this example, return:
        {'Cmd' : 'nav', 'responses' : '0', 'x' : '-5644', ...}

        Return a dictionary of response key/value pairs.

        """
        reply = dict()
        # split on | (bar)
        rlst = response.split('|')
        # handle Cmd=... first line specially
        rlst[0:1] = rlst[0].splitlines()
        # split key=val into key,val pairs
        for pair in rlst:
            (key,val) = pair.split('=')
            key = key.strip()
            val = val.strip()
            # try to convert to int
            try:
                val = int(val)
            except ValueError:
                pass
            reply[key] = val
        return reply

#     def getMCUReportValue(self):
#         # get the MCU report
#         report = str(self.getMCUReport());
#         # get the string that encodes (in hex) the status
#         status = report.split('\n')[1].split(' ')[2];
#         # return it
#         return status;

#     def getMCUReport(self):
#         print "getting MCUReport";
#         url = '%(prot)s://%(host)s/rev.cgi?Cmd=nav&action=20' % self.url_data
#         print "Getting Report";
#         return self.getRequestResponse(url);

#     def obstacle(self):
#         "Returns True if there's an obstacle, False otherwise"
#         # get just the status string from the MCU report
#         status = self.getMCUReportValue();
#         # get the last character, convert it to an integer
#         lastByte = int("0x" + status[len(status)-1], 16);
#         # the obstacle indicator is on bit 2
#         # take bitwise & with 00000100 (4 in base 10)
#         return ((lastByte & 4) > 0);

if __name__ == "__main__":
    pass
