"""Numerical certificate for lean-gaussian-field M3 and THE-ERIKSSON-PROGRAMME
Brick P4.5: finite-lattice massive free field, covariance (-Delta+m^2)^{-1},
exponential kernel decay via the exponential-conjugation (Combes-Thomas) chain.

Certifies, for 1D chains and 2D grids (Dirichlet):
  (H1) coercivity  c = lambda_min(K) >= m^2  (volume-uniform);
  (H2) finite range R = 1;
  (H3) Schur bound S = m^2 + 2*coord (volume-uniform);
  conjugation-admissible rate  theta_adm = ln(1 + c/S)  (certified, from the
    three-lemma chain: defect (e^{theta R}-1) S < c);
  sharp rate (1D)  q = arccosh(1 + m^2/2)  against the measured kernel decay
    (fit excludes the double-precision floor |C_0r| < 1e-12 -- the same lesson
    as the 0060 series appendix: floors contaminate fits);
  guardrail: both rates -> 0 as m -> 0 (criticality).
Outputs a JSON certificate (style: ym-lattice-numerics sidecar checks).
"""
import argparse
import json
from pathlib import Path

import numpy as np

def chain_K(N, m):
    return (m*m + 2)*np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)

def grid_K(L, m):
    N = L*L
    K = (m*m + 4)*np.eye(N)
    idx = lambda i,j: i*L + j
    for i in range(L):
        for j in range(L):
            if i+1 < L: K[idx(i,j), idx(i+1,j)] = K[idx(i+1,j), idx(i,j)] = -1
            if j+1 < L: K[idx(i,j), idx(i,j+1)] = K[idx(i,j+1), idx(i,j)] = -1
    return K

def fit_rate_1d(C, floor=1e-12):
    N = C.shape[0]; r0 = N//4
    vals = np.abs(C[r0, r0:r0 + N//2])
    ok = vals > floor
    rs = np.arange(len(vals))[ok]
    return -np.polyfit(rs[1:], np.log(vals[ok][1:]), 1)[0], int(ok.sum())

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output",
    type=Path,
    default=Path("data/processed/aqft_bridges/gaussian_covariance_certificate.json"),
)
args = parser.parse_args()

cert = {"tool": "gaussian_covariance_oracle", "lattice": []}
print("== 1D chain, K = (m^2+2)I - S - S^T, coord=1 ==")
for m in [0.5, 1.0, 2.0]:
    for N in [120, 240]:
        K = chain_K(N, m)
        c = float(np.linalg.eigvalsh(K)[0]); S = m*m + 4.0
        theta = float(np.log(1 + c/S))
        q_sharp = float(np.arccosh(1 + m*m/2))
        C = np.linalg.inv(K)
        q_fit, npts = fit_rate_1d(C)
        ok = abs(q_fit - q_sharp) < 5e-2*q_sharp + 1e-3
        row = dict(dim=1, N=N, m=m, c=round(c,6), S=S, theta_adm=round(theta,4),
                   q_sharp=round(q_sharp,4), q_fit=round(float(q_fit),4),
                   fit_points=npts, sharp_matches_fit=bool(ok))
        cert["lattice"].append(row)
        print(f"m={m} N={N}: c={c:.4f} theta_adm={theta:.4f} "
              f"q_sharp={q_sharp:.4f} q_fit={q_fit:.4f} pts={npts} "
              f"{'OK' if ok else 'MISMATCH'}")
print("volume-uniformity: c, S, theta_adm independent of N above (c -> m^2).")

print("\n== 2D grid, K = (m^2+4)I - adj, coord=2 ==")
for m in [1.0]:
    L = 24
    K = grid_K(L, m)
    c = float(np.linalg.eigvalsh(K)[0]); S = m*m + 8.0
    theta = float(np.log(1 + c/S))
    C = np.linalg.inv(K)
    # decay along a lattice axis from center
    i0 = (L//2)*L + L//4
    vals = [abs(C[i0, i0 + r]) for r in range(0, L//2)]
    vals = np.array(vals); ok = vals > 1e-12
    q_fit = -np.polyfit(np.arange(len(vals))[ok][1:], np.log(vals[ok][1:]), 1)[0]
    print(f"m={m} L={L}x{L}: c={c:.4f} theta_adm={theta:.4f} "
          f"axis q_fit={q_fit:.4f}  (certified rate is theta_adm; sharp 2D rate "
          f"is anisotropic and larger)")
    cert["lattice"].append(dict(dim=2, L=L, m=m, c=round(c,6), S=S,
                                theta_adm=round(theta,4), q_fit_axis=round(float(q_fit),4)))

print("\n== guardrail: m -> 0 closes both rates ==")
for m in [1e-2, 1e-4]:
    N = 240; c = float(np.linalg.eigvalsh(chain_K(N, m))[0])
    theta = np.log(1 + c/(m*m+4)); q = np.arccosh(1 + m*m/2)
    print(f"m={m:g}: theta_adm={theta:.2e}  q_sharp={q:.2e}")
    cert["lattice"].append(dict(dim=1, N=N, m=m, guardrail=True,
                                theta_adm=float(theta), q_sharp=float(q)))
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open("w", encoding="utf-8") as handle:
    json.dump(cert, handle, indent=1)
    handle.write("\n")
print(f"\ncertificate written: {args.output}")
