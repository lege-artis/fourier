#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Generate the Shad-tier dragon icon: Miyazaki-register, calm, smoking, tea in hand.
Saves dragon-icon.png to the same directory as this script.
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.path as mpath
Path = mpath.Path

OUT = pathlib.Path(__file__).resolve().parent / "dragon-icon.png"

fig, ax = plt.subplots(figsize=(4, 5), dpi=150)
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#f5f0e8")

# ── Palette ──────────────────────────────────────────────────────────────────
C_SCALE  = "#4a7c59"   # deep jade green (body)
C_LIGHT  = "#7ab892"   # lighter belly
C_ACCENT = "#c8956c"   # warm accent (horn, claws)
C_EYE    = "#1a1a2e"
C_SMOKE  = "#b0a898"
C_TEA    = "#c8956c"
C_CUP    = "#e8d5b0"
C_LINE   = "#2d3a2e"

def filled(verts, codes, fc, ec=C_LINE, lw=1.0, zorder=2, alpha=1.0):
    p = mpath.Path(verts, codes)
    ax.add_patch(mpatches.PathPatch(p, facecolor=fc, edgecolor=ec,
                                    linewidth=lw, zorder=zorder, alpha=alpha))

def bezier3(p0, p1, p2, p3):
    """Cubic bezier — verts + codes pair."""
    return ([p0, p1, p2, p3],
            [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])

# ── Tail ─────────────────────────────────────────────────────────────────────
tail_v = [(2.0, 1.0), (1.2, 1.8), (1.8, 2.6), (3.2, 2.5),
          (3.8, 2.3), (3.0, 1.6), (2.5, 1.1), (2.0, 1.0)]
tail_c = [Path.MOVETO] + [Path.CURVE3]*6 + [Path.CLOSEPOLY]
filled(tail_v, tail_c, C_SCALE, lw=0.8)

# ── Body (main torso S-curve) ─────────────────────────────────────────────────
body_v = [
    (2.8, 2.2),  # start lower-left
    (1.5, 3.5), (1.8, 5.5), (3.0, 6.2),   # left curve up
    (4.5, 7.0), (6.2, 6.8), (6.8, 5.5),   # right side top
    (7.2, 4.0), (6.5, 3.0), (5.0, 2.8),   # right side down
    (4.2, 2.6), (3.4, 2.0), (2.8, 2.2),   # close
]
body_c = ([Path.MOVETO] + [Path.CURVE4]*3 + [Path.CURVE4]*3 +
          [Path.CURVE4]*3 + [Path.LINETO]*2 + [Path.CLOSEPOLY])
filled(body_v, body_c, C_SCALE, lw=1.2, zorder=3)

# ── Belly (lighter underside) ─────────────────────────────────────────────────
belly_v = [
    (3.2, 2.8), (2.5, 4.0), (2.8, 5.8), (4.0, 6.0),
    (5.5, 5.8), (6.0, 4.5), (5.5, 3.2),
    (4.8, 2.9), (3.8, 2.7), (3.2, 2.8),
]
belly_c = ([Path.MOVETO] + [Path.CURVE4]*3 + [Path.CURVE4]*3 +
           [Path.LINETO]*2 + [Path.CLOSEPOLY])
filled(belly_v, belly_c, C_LIGHT, ec=C_LIGHT, lw=0, zorder=4, alpha=0.7)

# ── Wing (left, folded relaxed) ───────────────────────────────────────────────
wing_v = [
    (2.8, 5.5),               # root at shoulder
    (0.5, 7.5), (0.8, 9.0), (2.5, 8.5),
    (3.5, 7.8), (3.2, 6.5), (2.8, 5.5),
]
wing_c = ([Path.MOVETO] + [Path.CURVE4]*3 +
          [Path.CURVE4]*2 + [Path.CLOSEPOLY])
filled(wing_v, wing_c, C_SCALE, ec=C_LINE, lw=0.9, zorder=2, alpha=0.85)

# Wing membrane ribbing (3 thin bezier strokes)
for t in [0.3, 0.55, 0.78]:
    x0, y0 = 2.8, 5.5
    x1 = 0.5 + t * 2.3; y1 = 7.5 + t * 1.2
    ax.plot([x0, x1], [y0, y1], color=C_LINE, lw=0.5, alpha=0.4, zorder=3)

# ── Neck ─────────────────────────────────────────────────────────────────────
neck_v = [(4.0, 6.0), (3.5, 7.0), (4.0, 8.2), (5.0, 8.8),
          (5.8, 8.5), (5.5, 7.2), (5.0, 6.3), (4.0, 6.0)]
neck_c = [Path.MOVETO] + [Path.CURVE4]*6 + [Path.CLOSEPOLY]
filled(neck_v, neck_c, C_SCALE, lw=1.0, zorder=5)

# ── Head ─────────────────────────────────────────────────────────────────────
head = mpatches.Ellipse((5.5, 9.5), width=2.8, height=2.4,
                         angle=-10, facecolor=C_SCALE, edgecolor=C_LINE,
                         linewidth=1.2, zorder=6)
ax.add_patch(head)

# ── Snout / muzzle ───────────────────────────────────────────────────────────
snout_v = [(5.0, 8.9), (4.2, 8.6), (3.8, 9.0), (4.3, 9.5),
           (5.0, 9.6), (5.5, 9.3), (5.0, 8.9)]
snout_c = [Path.MOVETO] + [Path.CURVE3]*5 + [Path.CLOSEPOLY]
filled(snout_v, snout_c, C_LIGHT, ec=C_LINE, lw=0.8, zorder=7)

# ── Eye (left, slightly shut = amused) ───────────────────────────────────────
eye_outer = mpatches.Ellipse((5.9, 9.9), 0.55, 0.38,
                              facecolor="white", edgecolor=C_LINE, lw=0.8, zorder=8)
ax.add_patch(eye_outer)
eye_inner = mpatches.Ellipse((5.85, 9.88), 0.25, 0.22,
                              facecolor=C_EYE, edgecolor="none", zorder=9)
ax.add_patch(eye_inner)
# Eyelid (slight squint = amused)
lid_x = np.linspace(5.62, 6.18, 30)
lid_y = 9.90 + 0.13 * np.cos(np.linspace(-np.pi/2, np.pi/2, 30))
ax.plot(lid_x, lid_y, color=C_LINE, lw=1.0, zorder=10)
# Eye highlight
ax.plot(5.92, 9.95, "o", color="white", ms=2.5, zorder=11)

# ── Nostril ───────────────────────────────────────────────────────────────────
ax.plot(4.4, 9.15, "o", color=C_LINE, ms=2.0, zorder=8)

# ── Smile (subtle, knowing) ───────────────────────────────────────────────────
smile_x = np.linspace(4.3, 5.2, 40)
smile_y = 8.82 - 0.12 * np.sin(np.linspace(0, np.pi, 40))
ax.plot(smile_x, smile_y, color=C_LINE, lw=1.0, zorder=8)

# ── Horn ──────────────────────────────────────────────────────────────────────
horn_v = [(5.8, 10.55), (5.5, 11.4), (6.1, 11.6), (6.4, 10.7), (5.8, 10.55)]
horn_c = [Path.MOVETO] + [Path.CURVE3]*3 + [Path.CLOSEPOLY]
filled(horn_v, horn_c, C_ACCENT, ec=C_LINE, lw=0.8, zorder=7)

# ── Tiny crest spines ────────────────────────────────────────────────────────
for (x0, y0), (x1, y1) in [((4.6, 10.1), (4.3, 10.9)),
                             ((5.0, 10.3), (4.8, 11.1)),
                             ((5.4, 10.45), (5.2, 11.2))]:
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-", color=C_ACCENT,
                                lw=1.5, connectionstyle="arc3,rad=0.2"),
                zorder=7)

# ── Right arm holding tea cup ────────────────────────────────────────────────
arm_v = [(6.2, 4.5), (7.2, 4.0), (8.0, 3.5), (7.8, 3.0)]
arm_c = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
ax.add_patch(mpatches.PathPatch(mpath.Path(arm_v, arm_c),
             facecolor="none", edgecolor=C_SCALE, linewidth=3.5, zorder=5))
ax.add_patch(mpatches.PathPatch(mpath.Path(arm_v, arm_c),
             facecolor="none", edgecolor=C_LINE, linewidth=0.8, zorder=5))

# Tea cup
cup = mpatches.FancyBboxPatch((7.2, 2.3), 1.1, 0.75,
                               boxstyle="round,pad=0.08",
                               facecolor=C_CUP, edgecolor=C_LINE, lw=0.9, zorder=6)
ax.add_patch(cup)
# Cup handle
handle = mpatches.Arc((8.45, 2.67), 0.38, 0.45, theta1=-60, theta2=60,
                       color=C_LINE, lw=1.0, zorder=6)
ax.add_patch(handle)
# Tea surface (dark liquid)
tea_surf = mpatches.Ellipse((7.75, 3.02), 0.95, 0.22,
                             facecolor=C_TEA, edgecolor=C_LINE, lw=0.5, zorder=7)
ax.add_patch(tea_surf)
# Steam from tea
for dx, amp in [(-0.15, 0.12), (0.0, -0.10), (0.15, 0.09)]:
    sx = np.linspace(7.75 + dx, 7.75 + dx, 20)
    ty = np.linspace(3.15, 3.65, 20)
    sx = sx + amp * np.sin(np.linspace(0, 3*np.pi, 20))
    ax.plot(sx, ty, color=C_SMOKE, lw=0.9, alpha=0.6, zorder=6)

# ── Left arm — holding a thin joint ──────────────────────────────────────────
larm_v = [(4.0, 4.5), (3.0, 4.8), (2.2, 5.2), (1.9, 5.6)]
larm_c = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
ax.add_patch(mpatches.PathPatch(mpath.Path(larm_v, larm_c),
             facecolor="none", edgecolor=C_SCALE, linewidth=3.0, zorder=5))
ax.add_patch(mpatches.PathPatch(mpath.Path(larm_v, larm_c),
             facecolor="none", edgecolor=C_LINE, linewidth=0.8, zorder=5))
# Joint (small white cylinder)
joint_v = [(1.7, 5.5), (1.5, 5.85), (1.65, 5.92), (1.85, 5.58), (1.7, 5.5)]
joint_c = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
filled(joint_v, joint_c, "#f0ede4", ec=C_LINE, lw=0.7, zorder=7)
# Smoke from joint — lazy wisps drifting up-left
smoke_x_base = 1.60
for i, (offset, amp) in enumerate([(0, 0.18), (-0.08, -0.15), (0.06, 0.20)]):
    sy = np.linspace(6.0 + i*0.1, 8.2 + i*0.15, 40)
    sx = (smoke_x_base + offset +
          amp * np.sin(np.linspace(i * np.pi/3, i * np.pi/3 + 2.5*np.pi, 40)))
    alpha = 0.55 - i * 0.12
    ax.plot(sx, sy, color=C_SMOKE, lw=1.1 - i*0.15, alpha=alpha, zorder=3)

# ── Legs / feet (simple) ─────────────────────────────────────────────────────
for xb, side in [(3.3, 1), (5.0, -1)]:
    foot_v = [(xb, 2.2), (xb + side*0.3, 1.4),
              (xb + side*0.7, 1.0), (xb + side*1.1, 0.8)]
    foot_c = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    ax.add_patch(mpatches.PathPatch(mpath.Path(foot_v, foot_c),
                 facecolor="none", edgecolor=C_SCALE, linewidth=4.0, zorder=2))
    ax.add_patch(mpatches.PathPatch(mpath.Path(foot_v, foot_c),
                 facecolor="none", edgecolor=C_LINE, linewidth=0.8, zorder=2))
    # Three claws
    for claw_dx in [-0.15, 0.0, 0.15]:
        cx = xb + side*1.1 + claw_dx
        cy = 0.8
        ax.annotate("", xy=(cx + claw_dx*0.8, cy - 0.35),
                    xytext=(cx, cy),
                    arrowprops=dict(arrowstyle="-", color=C_ACCENT, lw=1.2),
                    zorder=3)

# ── Scale texture dots (subtle) ───────────────────────────────────────────────
rng = np.random.default_rng(42)
for _ in range(22):
    tx = rng.uniform(3.2, 6.5); ty = rng.uniform(3.0, 6.0)
    ax.plot(tx, ty, ".", color=C_LINE, ms=1.0, alpha=0.25, zorder=4)

fig.tight_layout(pad=0)
fig.savefig(str(OUT), dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.close(fig)
print(f"Dragon icon saved: {OUT}")
