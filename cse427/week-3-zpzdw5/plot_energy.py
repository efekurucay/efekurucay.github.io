import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sc = ["A\nNullRDC, 15 s", "B\nContikiMAC, 15 s", "C\nContikiMAC, 5 s"]
data = {  # mote: (CPU, LPM, TX, RX, I_avg)
 "Server (mote 1)": [(0.99,99.01,0.02,100.02,18.878),(1.84,98.16,0.52,0.89,0.344),(3.26,96.74,1.28,1.38,0.594)],
 "Client (mote 2)": [(1.08,98.92,0.02,100.02,18.881),(2.19,97.81,0.68,0.99,0.396),(4.15,95.85,1.75,1.65,0.743)],
}
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
w = 0.2; x = range(3)
cols = {"TX %":"#e4572e", "Listen %":"#4f7cac"}
ax = axes[0]
for j,(mote, rows) in enumerate(data.items()):
    for k,(name, idx) in enumerate([("TX %",2),("Listen %",3)]):
        vals = [r[idx] for r in rows]
        pos = [i + (j*2+k-1.5)*w for i in x]
        bars = ax.bar(pos, vals, w, color=cols[name], alpha=1 if j==0 else 0.55, label=f"{name} – {mote}")
        for p,v in zip(pos, vals): ax.text(p, v*1.15, f"{v:.2f}", ha="center", fontsize=7, rotation=90)
ax.set_yscale("log"); ax.set_ylim(0.01, 400); ax.set_xticks(list(x)); ax.set_xticklabels(sc)
ax.set_ylabel("% of time (log scale)"); ax.set_title("Radio TX and listen time per scenario")
ax.legend(fontsize=7, loc="upper right")
ax = axes[1]
for j,(mote, rows) in enumerate(data.items()):
    vals = [r[4] for r in rows]; pos = [i + (j-0.5)*0.35 for i in x]
    ax.bar(pos, vals, 0.35, color="#3a3a3a" if j==0 else "#9a9a9a", label=mote)
    for p,v in zip(pos, vals): ax.text(p, v*1.12, f"{v:.3f} mA\n{2500/v/24:.1f} d", ha="center", fontsize=8)
ax.set_yscale("log"); ax.set_ylim(0.1, 80); ax.set_xticks(list(x)); ax.set_xticklabels(sc)
ax.set_ylabel("Average current, mA (log scale)"); ax.set_title("Average current and lifetime (2500 mAh)")
ax.legend(fontsize=8)
fig.suptitle("Week 3 — Energy accounting in Cooja (Sky motes, 15 simulated minutes, first 2 intervals skipped)", fontsize=11)
fig.tight_layout(); fig.savefig("energy-graph.png", dpi=150)
print("ok")
