# pi-avr-control
Raspberry PI RS232 control 

Control a Sony AVR
Control a Sony projector



`cd /etc/systemd/system`

create x.service; modify

`sudo systemctl daemon-reload`

`sudo systemctl start x.service`

`sudo systemctl status x.service`

`sudo systemctl status x.service`

`sudo systemctl status x.service`

Todo: add .service files (unit files)<br>
Todo: check why mqtt client disconnects, reason for cronjobs

crontab

0 0 * * * sudo systemctl restart avr_control.service<br>
0 0 * * * sudo systemctl restart proj_control.service

