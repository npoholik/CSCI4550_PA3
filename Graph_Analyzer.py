import argparse
import re
import numpy as np
import matplotlib.pyplot as plt

def parse_mm_log(filepath):

    pattern = re.compile(r"(\d+(?:\.\d+)?)\s+([#\+\-])\s+(\d+)")
    times, evs, sizes = [], [], []
    with open(filepath, 'r') as f:
        for line in f:
            m = pattern.match(line.strip())
            if not m:
                continue
            t, ev, sz = m.groups()
            times.append(float(t))
            evs.append(ev)
            sizes.append(int(sz))
    return np.array(times), np.array(evs), np.array(sizes)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze mm-link logs for RTT, throughput, loss, and averages"
    )
    parser.add_argument('uplink_log', help='path to uplink (data) log')
    parser.add_argument('downlink_log', help='path to downlink (ACK) log')
    parser.add_argument('--bin-size', type=float, default=1.0,
                        help='time bin width (same units as timestamps)')
    parser.add_argument('--packet-size', type=int, default=1504,
                        help='bytes per data packet')
    args = parser.parse_args()

    # Parse logs
    up_t, up_ev, up_sz = parse_mm_log(args.uplink_log)
    dn_t, dn_ev, dn_sz = parse_mm_log(args.downlink_log)

    # Masks for events
    sent_mask = (up_ev == '#')
    drop_mask = (up_ev == '-')
    ack_mask  = (dn_ev == '#')

    sent_times = up_t[sent_mask]
    drop_times = up_t[drop_mask]
    ack_times  = dn_t[ack_mask]

    # Compute RTT values (match Nth packet send to Nth ACK)
    n = min(len(sent_times), len(ack_times))
    rtt_vals  = ack_times[:n] - sent_times[:n]
    rtt_times = sent_times[:n]

    # Define time bins
    if n > 0:
        start = min(sent_times.min(), ack_times.min())
        end   = max(sent_times.max(), ack_times.max())
    else:
        start, end = 0.0, 0.0
    bins = np.arange(start, end + args.bin_size, args.bin_size)

    # Throughput: bits/sec per bin
    sent_bytes_per_bin, _ = np.histogram(
        sent_times, bins=bins,
        weights=np.ones_like(sent_times) * args.packet_size)
    throughput = sent_bytes_per_bin * 8.0 / args.bin_size
    times_mid   = bins[:-1] + args.bin_size / 2.0

    # Loss rate: drops / (sends + drops) per bin
    drop_count, _ = np.histogram(drop_times, bins=bins)
    send_count, _ = np.histogram(sent_times, bins=bins)
    loss_rate = drop_count.astype(float) / (send_count + drop_count + 1e-9)

    # Compute averages
    avg_rtt = -np.mean(rtt_vals) if len(rtt_vals) > 0 else float('nan')
    total_sent_bytes = up_sz[sent_mask].sum()
    duration = end - start if end > start else float('nan')
    avg_throughput = (total_sent_bytes * 8.0 / duration) if duration > 0 else float('nan')

    # Print summary statistics
    print(f"Average RTT: {avg_rtt:.3f} (same time units as logs)")
    print(f"Average Throughput: {avg_throughput:.3f} bps over {duration:.3f} time units")

    # Plotting
    plt.figure()
    plt.plot(rtt_times, rtt_vals)
    plt.xlabel('Time')
    plt.ylabel('RTT')
    plt.title('RTT over Time')
    plt.grid(True)

    plt.figure()
    plt.plot(times_mid, throughput)
    plt.xlabel('Time')
    plt.ylabel('Throughput (bps)')
    plt.title('Throughput over Time')
    plt.grid(True)

    plt.figure()
    plt.plot(times_mid, loss_rate)
    plt.xlabel('Time')
    plt.ylabel('Loss Rate')
    plt.title('Loss Rate over Time')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
