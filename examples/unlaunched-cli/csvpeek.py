"""Print the first rows of a CSV file as an aligned table (example project for launchday's demo)."""
import csv
import sys

rows = list(csv.reader(open(sys.argv[1])))[:10]
widths = [max(len(r[i]) for r in rows if i < len(r)) for i in range(len(rows[0]))]
for r in rows:
    print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
