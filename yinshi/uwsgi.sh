killall -9 uwsgi
uwsgi -b 10000 -x django.xml --daemonize django.log
