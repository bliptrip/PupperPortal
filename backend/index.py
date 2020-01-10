#!/usr/bin/env python3
try:
    from flask import Flask, Response, stream_with_context
except ImportError:
    exit("This script requires the flask module\nInstall with: sudo pip install flask")
import motors
import signal
import subprocess as sp
import os
import sys

app = Flask(__name__)
pt = None #Pan tilt object

#Camera streaming and control API
pipe = None
@app.route('/camera/stream/live.webm', methods=['GET'])
def camera_view():
    def generate_content():
        pipe = sp.Popen(['./gst_cam_stream.sh'], shell=True, stdout=sp.PIPE, stderr=sys.stderr, preexec_fn=os.setsid)
        print("pipe is: {}".format(pipe))
        try:
            while True:
                data = pipe.stdout.read(8192)
                yield(data)
        except GeneratorExit:
            os.killpg(pipe.pid,signal.SIGTERM)
            print("closed")
    return(stream_with_context(Response(generate_content(), mimetype='video/webm')))


@app.route('/motors/init')
def motors_init():
    global pt
    pt = motors.PanTilt() 
    return('')

@app.route('/motors/cleanup')
def motors_cleanup():
    global pt
    del(pt)
    pt = None
    return('')

@app.route('/motors/move/<direction>/<steps>')
def motors_move(direction,steps):
    global pt
    steps = int(steps)
    if pt is not None:
        if (direction == 'up') or (direction == 'down'):
            axis = 1
        if (direction == 'left') or (direction == 'right'):
            axis = 0
        if (direction == 'up') or (direction == 'right'):
            steps = -1 * steps
        pt.rotate(axis, steps)
    return('')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
