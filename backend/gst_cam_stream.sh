#!/bin/bash

raspivid -n -hf -vf -ih -fl -t 0 -fps 10 --mode 4 -awb auto -ex night -mm backlit --mode 4 -br 50 -o - | gst-launch-1.0 -v fdsrc do-timestamp=true fd=0 ! h264parse ! matroskamux streamable=true ! fdsink fd=4 4>&1 1>&2
