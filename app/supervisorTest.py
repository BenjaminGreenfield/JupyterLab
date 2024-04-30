import subprocess
import io
import time
#import cv2

from PIL import Image
from flask import Flask, Response
from Xlib import display, X
#import numpy as np

app = Flask(__name__)

def get_xvfb_screen():
    dsp = display.Display(':1')
    root = dsp.screen().root
    screen = dsp.screen()
    depth = screen.root_depth
    print(f"Depth of the screen: {depth} bits")
    
    while True:
        geom = root.get_geometry()
        width = geom.width
        height = geom.height

        # Fetch the raw image data from the root window
        raw = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)

        if depth == 16:
            image = Image.frombytes("RGB", (width, height), raw.data, "raw", "RGB;16")
        
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=50)
        screen_data = buffer.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + screen_data + b'\r\n')

        time.sleep(1)
        
@app.route('/video_feed')
def video_feed():
    return Response(get_xvfb_screen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    # HTML page to display the live video stream
    return '''
    <html>
    <head>
        <title>VNC Viewer Stream</title>
    </head>
    <body>
        <h1>VNC Viewer Stream</h1>
        <img src="/video_feed" />
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)