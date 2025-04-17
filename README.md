Commands used to initialize the process:


Move to tests:

Example: 50 Mbps BBR Test:

python2 generate_trace.py 50 10 60 50mbps_data.trace

mm-link 50mbps_data.trace 50mbps_ack.trace   --uplink-log=../experiment_logs/BRR_50/50mbps_datalink.log   --downlink-log=../experiment_logs/BRR_50/50mbps_acklink.log --   python2 ../src/experiments/Tunnel_manager_updated.py --auto-test --scheme brr --data-dir experiment_logs/50mbps_bbr

python2 Analyze_Metrics.py ../experiment_logs/BRR_50/50mbps_datalink.log ../experiment_logs/rttevents.log ../experiment_logs/sent.log ../experiment_logs/recv.log



Clear log files after each test in order to avoid issues with overlapping data.
Review log files to determine key statistics and trends. 
