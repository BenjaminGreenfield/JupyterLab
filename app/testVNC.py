from flask import Flask, Response
from vncdotool import api

import io

app = Flask(__name__)

def get_vnc_screen():
#    client = api.connect('192.168.1.181::5900', password='54') boop
    client = api.connect('vnc://192.168.1.181:5900', password='5424978168')
    while True:
        # Capture the screen as an image object, save to a buffer, and yield it
        client.refreshScreen()
        image = client.screen.copy()
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG')
        screen_data = buffer.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + screen_data + b'\r\n')
    client.disconnect()

@app.route('/video_feed')
def video_feed():
    return Response(get_vnc_screen(),
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
