"""Turn a saved Cooja Mote Output log into the week 3 energy table.

    python3 powertrace_to_csv.py scenario-a.txt scenario-a.csv

Each Powertrace line carries cumulative Energest tick counters. The script takes the
difference between consecutive lines of the same mote and writes one CSV row per
interval: Time, Mote, CPU %, LPM %, TX %, RX %, Radio On %. It then prints, per mote,
the averages after the warm-up, the average current and a rough lifetime, plus the
packet delivery ratio counted from the client's "TX:" and the server's
"Server received:" lines.
"""
import argparse
import csv
import re
from collections import defaultdict

# <cooja time> ID:<mote> <clock ticks> P <addr> <seqno> <all_cpu> <all_lpm> <all_tx> <all_listen> ...
POWERTRACE = re.compile(r"ID:(\d+)\s+(\d+) P \d+\.\d+ \d+ (\d+) (\d+) (\d+) (\d+) ")
SENT = re.compile(r"ID:\d+\s+TX: Hello (\d+) ")
RECEIVED = re.compile(r"ID:\d+\s+Server received: 'Hello (\d+) ")

# Current model from the lab deck, in mA.
CURRENT_MA = {"cpu": 1.8, "lpm": 0.0545, "tx": 17.4, "rx": 18.8}


def parse(path, clock_second):
    rows = []
    previous = defaultdict(lambda: (0, 0, 0, 0))
    sent, received = set(), set()
    with open(path, encoding="utf-8", errors="replace") as log:
        for line in log:
            if m := SENT.search(line):
                sent.add(int(m.group(1)))
            elif m := RECEIVED.search(line):
                received.add(int(m.group(1)))
            elif m := POWERTRACE.search(line):
                mote, clock, *counters = map(int, m.groups())
                d_cpu, d_lpm, d_tx, d_rx = (now - before for now, before in zip(counters, previous[mote]))
                previous[mote] = tuple(counters)
                total = d_cpu + d_lpm
                if total <= 0:
                    continue
                rows.append({
                    "Time": round(clock / clock_second),
                    "Mote": mote,
                    "CPU %": 100 * d_cpu / total,
                    "LPM %": 100 * d_lpm / total,
                    "TX %": 100 * d_tx / total,
                    "RX %": 100 * d_rx / total,
                    "Radio On %": 100 * (d_tx + d_rx) / total,
                })
    return rows, sent, received


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("log", help="Mote Output saved from Cooja (File > Save to file)")
    parser.add_argument("csv", help="CSV file to write")
    parser.add_argument("--skip", type=int, default=2, help="warm-up intervals to leave out of the averages (default 2)")
    parser.add_argument("--battery-mah", type=float, default=2500, help="battery capacity for the lifetime estimate (default 2500, two AA cells)")
    parser.add_argument("--clock-second", type=int, default=128, help="clock ticks per second (128 on Sky)")
    args = parser.parse_args()

    rows, sent, received = parse(args.log, args.clock_second)
    if not rows:
        raise SystemExit(f"No Powertrace lines found in {args.log}")

    columns = ["Time", "Mote", "CPU %", "LPM %", "TX %", "RX %", "Radio On %"]
    with open(args.csv, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.2f}" if isinstance(v, float) else v) for k, v in row.items()})

    by_mote = defaultdict(list)
    for row in rows:
        by_mote[row["Mote"]].append(row)
    for mote, intervals in sorted(by_mote.items()):
        steady = intervals[args.skip:] or intervals
        mean = {c: sum(r[c] for r in steady) / len(steady) for c in columns[2:]}
        current = (mean["CPU %"] * CURRENT_MA["cpu"] + mean["LPM %"] * CURRENT_MA["lpm"]
                   + mean["TX %"] * CURRENT_MA["tx"] + mean["RX %"] * CURRENT_MA["rx"]) / 100
        hours = args.battery_mah / current
        print(f"Mote {mote}: {len(steady)} intervals | "
              + " | ".join(f"{c} {mean[c]:.2f}" for c in columns[2:])
              + f" | I_avg {current:.3f} mA | lifetime {hours:.0f} h = {hours / 24:.1f} days")
    if sent:
        delivered = len(sent & received)
        print(f"PDR: {delivered}/{len(sent)} = {delivered / len(sent):.2f}")


if __name__ == "__main__":
    main()
