#!/usr/bin/python3

import argparse
import json
import logging
import os, sys

from datetime import datetime

# NAGIOS return codes :
# https://nagios-plugins.org/doc/guidelines.html#AEN78
OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = 3

mylogger = logging.getLogger(__name__)

def debug_factory(logger, debug_level):
   """
   Decorate logger in order to add custom levels for Nagios
   """
   def custom_debug(msg, *args, **kwargs):
       if logger.level >= debug_level:
           return
       logger._log(debug_level, msg, args, kwargs)
   return custom_debug


def get_args():
   """
   Supports the command-line arguments listed below.
   """
   parser = argparse.ArgumentParser(description="Nagios borgbackup repository check")
   parser._optionals.title = "Options"
   parser.add_argument('-H', required=False, help='Dummyost for Librenms', dest='host', type=str, default='')
   parser.add_argument('-r', '--repository', required=False, help='Repository to check', dest='repo', type=str, default='')
   parser.add_argument('-c', '--config-file', required=False, help='Borgmatic configfile', dest='config', type=str, default='')
   parser.add_argument('-a', '--archive', required=False, help='Archive to check', dest='archive', type=str, default='latest')
   parser.add_argument('-d', '--overdue', nargs=1, required=False, help='time to mark repository as overdue in hours', dest='overdue', type=int, default=[24])
   parser.add_argument('-v', '--verbose', required=False, help='enable verbose output', dest='verbose', action='store_true')
   parser.add_argument('--borgmatic', required=False, help='alternitiv path to borgmatic', dest='borgmatic', type=str, default='/usr/local/bin/borgmatic')
   parser.add_argument('--log-file', nargs=1, required=False, help='file to log to (default = stdout)', dest='logfile', type=str)
   parser.add_argument('--nagios', required=False, help='enable nagios output mode', dest='nagios_output', action='store_true')
   parser.add_argument('--run-as-root', required=False, help='run borgmatic command with sudo', dest='sudo', action='store_true')
   parser.add_argument('--stats', required=False, help='Send perf data', dest='stats', action='store_true')

   args = parser.parse_args()
   return args

def size_format(b):
   """
   Format bytes to human readable values
   """
   if b < 1000:
             return '%i' % b + ' B'
   elif 1000 <= b < 1000000:
       return '%.1f' % float(b/1000) + ' KB'
   elif 1000000 <= b < 1000000000:
       return '%.1f' % float(b/1000000) + ' MB'
   elif 1000000000 <= b < 1000000000000:
       return '%.1f' % float(b/1000000000) + ' GB'
   elif 1000000000000 <= b:
       return '%.1f' % float(b/1000000000000) + ' TB'

def main():
   """
   CMD Line tool
   """
   # Handling arguments
   args          = get_args()
   overdue       = args.overdue[0]
   verbose       = args.verbose
   nagios_output = args.nagios_output
   repo          = f"--repository {args.repo}" if args.repo != "" else ""
   config        = f"-c {args.config}" if args.config != "" else ""
   archive       = args.archive
   borgmatic     = args.borgmatic
   sudo          = f"sudo " if args.sudo else ""
   stats         = args.stats

   # Building borgmatic commandstring
   cmd_bm_info = f"{sudo}{borgmatic} info --json {config} --archive {archive} {repo}"

   log_file = None
   if args.logfile:
       log_file = args.logfile[0]

   # Logging settings
   if verbose:
       log_level = logging.DEBUG
   else:
       log_level = logging.INFO

   if nagios_output:
       # Add custom level unknown
       logging.addLevelName(logging.DEBUG+1, 'UNKOWN')
       setattr(mylogger, 'unkown', debug_factory(mylogger, logging.DEBUG+1))

       # Change INFO LevelName to OK
       logging.addLevelName(logging.INFO, 'OK')

       # Setting output format for Nagios
       logging.basicConfig(filename=log_file,format='%(message)s',level=logging.INFO)
   else:
       logging.basicConfig(filename=log_file,format='%(asctime)s %(message)s',level=log_level)


   #####################################
   # Bork Repository Overdue Check     #
   #####################################

   mylogger.debug("Running os command line : %s" % cmd_bm_info)
   bm_info_json = json.loads(os.popen(cmd_bm_info).readline().strip())

   # Parsing Values from JSON
   arch_end      = datetime.strptime(bm_info_json[0]['archives'][0]['end'], '%Y-%m-%dT%H:%M:%S.000000')
   arch_age      = round((datetime.now() - arch_end).total_seconds()/3600, 1)

   if stats:
       arch_duration = bm_info_json[0]['archives'][0]['duration']
       arch_cmp_size = size_format(bm_info_json[0]['archives'][0]['stats']['compressed_size'])
       arch_org_size = size_format(bm_info_json[0]['archives'][0]['stats']['original_size'])
       arch_ded_size = size_format(bm_info_json[0]['archives'][0]['stats']['deduplicated_size'])

       perf_data = f" | duration={arch_duration} s, compressed_size={arch_cmp_size}, original_size={arch_org_size}, deduplicated_size={arch_ded_size}"
   else:
       perf_data = ""

   if arch_age < overdue:
       msg = f"BORG OK: {arch_age}h since last backup.{perf_data}"
       if nagios_output:
           print(msg)
       else:
           mylogger.info(msg)
       sys.exit(OK)

   elif arch_age == overdue:
       msg = f"BORG WARNING: {arch_age}h since last backup. Archive will become overdue soon!{perf_data}"
       if nagios_output:
           print(msg)
       else:
           mylogger.warning(msg)
       sys.exit(WARNING)

   elif arch_age > overdue:
       msg = f"BORG: CRITICAL: {arch_age}h since last backup. {arch_age-overdue}h overdue!{perf_data}"
       if nagios_output:
           print(msg)
       else:
           mylogger.critical(msq)
       sys.exit(CRITICAL)

   else:
       msg = f"BORG UNKNOWN: {arch_age}h since last backup.{perf_data}"
       if nagios_output:
           print(msg)
       else:
           mylogger.unkown(msg)
       sys.exit(UNKNOWN)

if __name__ == "__main__":
  main()
