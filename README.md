# check_borg
This is a simpkle Nagios plugin to monitor borg backups using borgmatic. It has an centralized approch, Monitoring everything from the host the script is running. 

Make shure borgmnatic can talk to your Repos. this coul be a possible call: `--run-as-root -c /etc/borgmatic/librenms.yaml --stats -r ssh://backup/home/backups/ds.star.home --nagios`

```
usage: check_borg [-h] [-H HOST] [-r REPO] [-c CONFIG] [-a ARCHIVE] [-d OVERDUE] [-v] [--borgmatic BORGMATIC]
                  [--log-file LOGFILE] [--nagios] [--run-as-root] [--stats]

Nagios borgbackup repository check

Options:
  -h, --help            show this help message and exit
  -H HOST               Dummyost for Librenms
  -r REPO, --repository REPO
                        Repository to check
  -c CONFIG, --config-file CONFIG
                        Borgmatic configfile
  -a ARCHIVE, --archive ARCHIVE
                        Archive to check
  -d OVERDUE, --overdue OVERDUE
                        time to mark repository as overdue in hours
  -v, --verbose         enable verbose output
  --borgmatic BORGMATIC
                        alternitiv path to borgmatic
  --log-file LOGFILE    file to log to (default = stdout)
  --nagios              enable nagios output mode
  --run-as-root         run borgmatic command with sudo
  --stats               Send perf data
```


if running borg as root make sure to grant only the nessesary priviliges in `\etc\sudoers` like in this example: 
`librenms  ALL=(root) NOPASSWD: /usr/local/bin/borgmatic` 
