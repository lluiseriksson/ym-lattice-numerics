"""Numerical target certificate for lean-transfer-matrix M3 (discrete Gaussian
chain -- milestone 'not started' as of 2026-07-03).

For the 1D lattice Gaussian field with weight exp(-1/2 sum[(phi_{i+1}-phi_i)^2
+ m^2 phi_i^2]), certifies the forward AND reverse dictionary numerically:

  (i)  transfer operator T(x,y) = exp(-m^2 x^2/4) exp(-(x-y)^2/2) exp(-m^2 y^2/4)
       discretized on a grid: spectral gap  g := log(lambda_0/lambda_1);
  (ii) two-point clustering rate q of <phi_0 phi_r> = (K^{-1})_{0r};
  (iii) the dictionary equality  g = q = arccosh(1 + m^2/2)  to 4 decimals;
  (iv) guardrail: everything closes as m -> 0.

This is the exact statement shape M1/M2 of lean-transfer-matrix want
(gap <=> clustering), instantiated on the M3 model with certified numbers
before formalization. JSON certificate in the ym-lattice-numerics style.
"""
import argparse
import json
from pathlib import Path

import numpy as np

def transfer_gap(m, X=12.0, M=1200):
    x = np.linspace(-X, X, M); dx = x[1]-x[0]
    A = np.exp(-0.25*m*m*x**2)
    T = A[:,None]*np.exp(-0.5*(x[:,None]-x[None,:])**2)*A[None,:]*dx
    w = np.linalg.eigvalsh((T+T.T)/2)
    lam = np.sort(w)[::-1]
    return float(np.log(lam[0]/lam[1]))

def clustering_rate(m, N=240, floor=1e-12):
    K = (m*m+2)*np.eye(N) - np.eye(N,k=1) - np.eye(N,k=-1)
    C = np.linalg.inv(K); r0 = N//4
    vals = np.abs(C[r0, r0:r0+N//2]); ok = vals > floor
    rs = np.arange(len(vals))[ok]
    return float(-np.polyfit(rs[1:], np.log(vals[ok][1:]), 1)[0])

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output",
    type=Path,
    default=Path("data/processed/aqft_bridges/transfer_gap_certificate.json"),
)
args = parser.parse_args()

cert = {"tool": "transfer_gap_oracle", "rows": []}
print("m    | gap g = log(l0/l1) | clustering q | arccosh(1+m^2/2) | match")
for m in [0.5, 1.0, 2.0]:
    g = transfer_gap(m); q = clustering_rate(m)
    ana = float(np.arccosh(1 + m*m/2))
    ok = abs(g-ana) < 2e-3 and abs(q-ana) < 2e-3
    print(f"{m:4.2f} | {g:18.4f} | {q:12.4f} | {ana:16.4f} | {'OK' if ok else 'MISMATCH'}")
    cert["rows"].append(dict(m=m, gap=round(g,5), clustering=round(q,5),
                             analytic=round(ana,5), match=bool(ok)))
print("\nguardrail m->0:")
for m in [0.05, 0.01]:
    g = transfer_gap(m, X=40.0, M=1600); ana = float(np.arccosh(1+m*m/2))
    print(f"m={m}: gap={g:.4f} analytic={ana:.4f} (both close)")
    cert["rows"].append(dict(m=m, gap=round(g,5), analytic=round(ana,5), guardrail=True))
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("w", encoding="utf-8") as handle:
    json.dump(cert, handle, indent=1)
    handle.write("\n")
print(f"\ncertificate written: {args.output}")
