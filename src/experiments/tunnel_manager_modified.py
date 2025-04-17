import os
from os import path
import sys
import signal
import time
from subprocess import Popen, PIPE

import context
from helpers import utils

packets_sent = 0
packets_acked = 0

RTT_LOG = "../experiment_logs/rttevents.log"
SENT_LOG = "../experiment_logs/sent.log"
RECV_LOG = "../experiment_logs/recv.log"


def log_event(log_file, message):
   with open(log_file, "a") as f:
       f.write(message + "\n")


def auto_test(duration=60, interval=0.1, tun_id=1, procs={}):
   global packets_sent, packets_acked
   end_time = time.time() + duration

   sys.stdout.write("Starting auto-test for %d seconds, sending a packet every %.2f seconds...\n" % (duration, interval))
   sys.stdout.flush()
  
   while time.time() < end_time:
       t_send = time.time()
       log_event(SENT_LOG, "%.6f" % t_send)
       packets_sent += 1

       try:
           procs[tun_id].stdin.write("send_packet\n")
           procs[tun_id].stdin.flush()
       except Exception as e:
           sys.stderr.write("Error sending packet command: %s\n" % e)
           break

       ack = procs[tun_id].stdout.readline().strip()
       if not ack:
           sys.stderr.write("No ACK received for packet from tunnel %d\n" % tun_id)
       else:
           t_ack = time.time()
           packets_acked += 1
           log_event(RECV_LOG, "%.6f" % t_ack)

           rtt_ms = (t_ack - t_send) * 1000.0
           log_event(RTT_LOG, "%.6f %.6f %.2f" % (t_send, t_ack, rtt_ms))
           sys.stdout.write("RTT for packet: %.2f ms\n" % rtt_ms)
           sys.stdout.flush()
       time.sleep(interval)
   sys.stdout.write("Auto-test completed. Total packets sent: %d, ACKed: %d\n" % (packets_sent, packets_acked))
   sys.stdout.flush()


def main():
   prompt = ''
   procs = {}

   auto_mode = False
   auto_duration = 60  
   auto_interval = 0.1 
   if '--auto-test' in sys.argv:
       auto_mode = True

   def stop_signal_handler(signum, frame):
       for tun_id in procs:
           utils.kill_proc_group(procs[tun_id])
       sys.exit('tunnel_manager: caught signal %s and cleaned up\n' % signum)


   signal.signal(signal.SIGINT, stop_signal_handler)
   signal.signal(signal.SIGTERM, stop_signal_handler)


   sys.stdout.write('tunnel manager is running\n')
   sys.stdout.flush()

   if auto_mode:
       if 1 not in procs:
           sys.stderr.write("No tunnel process with ID 1 found; launching dummy tunnel client...\n")
           dummy_client = os.path.join(os.getcwd(),"../" "src", "wrappers", "ack_client.py")
           cmd_to_run = ["python2", dummy_client]
           procs[1] = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
          
           time.sleep(1)
           sys.stderr.write("Tunnel process with ID 1 launched using dummy tunnel client.\n")
       auto_test(duration=auto_duration, interval=auto_interval, tun_id=1, procs=procs)
       sys.exit(0)

   while True:
       input_cmd = sys.stdin.readline().strip()
       if not input_cmd:
           continue 
       if prompt:
           sys.stderr.write(prompt + ' ')
       sys.stderr.write(input_cmd + '\n')
       sys.stderr.flush()
       cmd = input_cmd.split()


       if not cmd:
           continue


       if cmd[0] == 'tunnel':
           if len(cmd) < 3:
               sys.stderr.write('error: usage: tunnel ID CMD...\n')
               continue
           try:
               tun_id = int(cmd[1])
           except ValueError:
               sys.stderr.write('error: usage: tunnel ID CMD...\n')
               continue
           cmd_to_run = ' '.join(cmd[2:])
           if cmd[2] == 'mm-tunnelclient' or cmd[2] == 'mm-tunnelserver':
               cmd_to_run = path.expandvars(cmd_to_run).split()
               for i in xrange(len(cmd_to_run)):
                   if ('--ingress-log' in cmd_to_run[i] or '--egress-log' in cmd_to_run[i]):
                       t = cmd_to_run[i].split('=')
                       cmd_to_run[i] = t[0] + '=' + path.expanduser(t[1])
               procs[tun_id] = Popen(cmd_to_run, stdin=PIPE, stdout=PIPE, preexec_fn=os.setsid)
           elif cmd[2] == 'python': 
               if tun_id not in procs:
                   sys.stderr.write('error: run tunnel client or server first\n')
                   continue
               procs[tun_id].stdin.write(cmd_to_run + '\n')
               procs[tun_id].stdin.flush()
           elif cmd[2] == 'readline':
               if len(cmd) != 3:
                   sys.stderr.write('error: usage: tunnel ID readline\n')
                   continue
               if tun_id not in procs:
                   sys.stderr.write('error: run tunnel client or server first\n')
                   continue
               sys.stdout.write(procs[tun_id].stdout.readline())
               sys.stdout.flush()
           else:
               sys.stderr.write('unknown command after "tunnel ID": %s\n' % cmd_to_run)
               continue
       elif cmd[0] == 'prompt':
           if len(cmd) != 2:
               sys.stderr.write('error: usage: prompt PROMPT\n')
               continue
           prompt = cmd[1].strip()
       elif cmd[0] == 'halt':
           if len(cmd) != 1:
               sys.stderr.write('error: usage: halt\n')
               continue
           for tun_id in procs:
               utils.kill_proc_group(procs[tun_id])
           sys.exit(0)
       else:
           sys.stderr.write('unknown command: %s\n' % input_cmd)
           continue


if __name__ == '__main__':
   main()
