# check_borg
This is a simpkle Nagios plugin to monitor borg backups using borgmatic. It has an centralized approch, Monitoring everything from the host the script is running. 

Make shure borgmnatic can talk to your Repos. this coul be a possible call: `--run-as-root -c /etc/borgmatic/librenms.yaml --stats -r ssh://backup/home/backups/ds.star.home --nagios`


