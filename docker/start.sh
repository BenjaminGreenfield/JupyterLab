#!/bin/bash
# Start SSH Daemon
/usr/sbin/sshd -D &

cp /docker/configs/xvfb.conf /etc/supervisor/conf.d/
supervisord -c /etc/supervisor/supervisord.conf


# Start Jupyter Lab
exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

