import os
import subprocess

import io
import time
#import cv2

# Set DISPLAY environment variable
os.environ['DISPLAY'] = ':1'

#from PIL import Image
from PIL import ImageGrab, Image, ImageDraw

from flask import Flask, Response
from flask import render_template

from flask_socketio import SocketIO, emit

from Xlib import display, X, XK
from Xlib.ext import xtest

from Xlib.ext.xtest import fake_input

#import numpy as np

app = Flask(__name__)

socketio = SocketIO(app)


def get_xvfb_screen():
    dsp = display.Display(':1')
    root = dsp.screen().root
    screen = dsp.screen()
    depth = screen.root_depth
    print(f"Depth of the screen: {depth} bits")

    cursor = Image.new('RGBA', (20, 20), (255, 0, 0, 0))  # Create a simple red cursor
    draw = ImageDraw.Draw(cursor)
    draw.line((10, 0, 10, 20), fill="red", width=2)  # Vertical line
    draw.line((0, 10, 20, 10), fill="red", width=2)  # Horizontal line

    
    @socketio.on('mousemove')
    def handle_mousemove(message):
        x, y = message['x'], message['y']
        # Ensure x, y are within your screen's bounds
        screen_width = dsp.screen().width_in_pixels
        screen_height = dsp.screen().height_in_pixels
    
        # Scaling the coordinates if necessary (example assumes 1920x1080 resolution)
#        x = int(x * screen_width / 1920)
#        y = int(y * screen_height / 1080)

 #       print(f"Moving pointer to ({x}, {y})")  # Debug output
        root.warp_pointer(x, y)

        dsp.flush()   

        # Get the current mouse position
#        print( "mouse " , x, y  )
#        data = dsp.screen().root.query_pointer()._data
#        print("Mouse position:", data["root_x"], data["root_y"])        

    @socketio.on('keypress')
    def handle_keypress(message):
        key = message['key']

        if key == 'q':
            print( "mouse click" )
            fake_input(dsp, X.ButtonPress, 1)  # 1 is the button code for left click
            dsp.sync()
        if key == 'w':
            print( "mouse release" )
            fake_input(dsp, X.ButtonRelease, 1) 
            dsp.sync()


        # Convert the string key to a keysym
        keysym = XK.string_to_keysym(key)

#        keysym = XK.string_to_keysym("Return")
        
        # Convert keysym to keycode
        keycode = dsp.keysym_to_keycode(keysym)

#        print( "keycode:" , keycode );

        if keycode:
            # Simulate key press
            xtest.fake_input(dsp, X.KeyPress, keycode)
            dsp.flush()  # Ensure that X11 receives the command
            dsp.sync()
            
            # Simulate key release
            xtest.fake_input(dsp, X.KeyRelease, keycode)
            dsp.flush()  # Ensure that X11 receives the command  
            dsp.sync()
    
    while True:
        geom = root.get_geometry()
        width = geom.width
        height = geom.height

        # Fetch the raw image data from the root window
        raw = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)

        if depth == 16:
            image = Image.frombytes("RGB", (width, height), raw.data, "raw", "RGB;16")

        # Paste the cursor image onto the screenshot at the mouse position
        data = dsp.screen().root.query_pointer()._data
#        print("Mouse position:", data["root_x"], data["root_y"])        
        image.paste(cursor, (data["root_x"], data["root_y"]), cursor)
    
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=50)
        screen_data = buffer.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + screen_data + b'\r\n')

#        time.sleep(0.1)
        
@app.route('/video_feed')
def video_feed():
    return Response(get_xvfb_screen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


#@app.route('/')
#def index():
#    # HTML page to display the live video stream
#    return '''
#    <html>
#    <head>
#        <title>VNC Viewer Stream</title>
#    </head>
#    <body>
#        <h1>VNC Viewer Stream</h1>
#        <img src="/video_feed" />
#    </body>
#    </html>
#    '''
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000 )
#    app.run(host='0.0.0.0', port=5000, threaded=True)
