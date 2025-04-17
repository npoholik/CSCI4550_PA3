import sys, time


while True:
   try:
       line = raw_input("> ")
   except EOFError:
       break

   #Modify time for RTT
   time.sleep(0.199)
   sys.stdout.write("ACK\n")
   sys.stdout.flush()
