# pi-avr-control
Raspberry PI RS232 control 

Control a Sony AVR
Control a Sony projector



cd /etc/systemd/system

create x.service; modify

sudo systemctl daemon-reload

sudo systemctl start x.service

sudo systemctl status example.service

sudo systemctl status example.service

sudo systemctl status example.service

Todo: add .service files (unit files)

crontab

0 0 * * * sudo systemctl restart avr_control.service
0 0 * * * sudo systemctl restart proj_control.service

