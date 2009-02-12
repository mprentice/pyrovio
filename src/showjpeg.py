import cStringIO
import wx
import urllib2, base64

# set up Rovio and get jpeg
username = "mprentice"
password = "ecitnerp"
uri = "192.168.1.101"
port = 80
url_prefix = "http://" + uri + ":" + str(port) + "/"
jpeg_url = url_prefix + "Jpeg/CamImg.jpg"
print jpeg_url

req = urllib2.Request(jpeg_url)
if username is not None:
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req.add_header("Authorization", "Basic %s" % base64string)
response = urllib2.urlopen(req)
jpeg_data = response.read()
#print jpeg_data
jpeg_stream = cStringIO.StringIO(jpeg_data)

# f = file('tmp.jpg', 'wb')
# f.write(jpeg_data)
# f.close()

# f = file('tmp.jpg', 'rb')
# file_image = wx.ImageFromStream(f, wx.BITMAP_TYPE_JPEG)
# f.close()

a = wx.PySimpleApp()
# wximg = wx.Image('/Users/mprentice/Sites/downloads/photos/dana_in_jeans.jpg',
#                  wx.BITMAP_TYPE_JPEG)
# wximg = wx.Image(jpeg_url, wx.BITMAP_TYPE_JPEG)
wximg = wx.ImageFromStream(jpeg_stream, wx.BITMAP_TYPE_JPEG)
wxbmp = wximg.ConvertToBitmap()
f = wx.Frame(None, -1, "Show JPEG demo")
f.SetSize( wxbmp.GetSize() )
wx.StaticBitmap(f,-1,wxbmp,(0,0))
f.Show(True)
def callback(evt,a=a,f=f):
    # Closes the window upon any keypress
    f.Close()
    a.ExitMainLoop()
wx.EVT_CHAR(f,callback)
a.MainLoop()
