import numpy as np
from scipy.ndimage import label, binary_opening

# ============================================================
# USER PARAMETERS (ADJUST PER SURVEY)
# ============================================================

FLARE_THRESHOLD_DB = -40          # strong gas return
MIN_PLUME_HEIGHT_M = 20           # minimum plume height
VERTICAL_FILTER = 6               # samples
TXT_OUTPUT = "kongsberg_gas_flares.txt"

# ============================================================
# INPUT DATA (FROM KONGSBERG DECODER)
# ============================================================
# These are assumed to come from pyall / pysonar / netCDF

# Sv in dB: shape (ping, sample, beam)
sv_db = wc_sv_db  

# Geometry
beam_angles_deg = beam_angles
ranges_m = sample_ranges

# Navigation (per ping)
x_ping = nav_x
y_ping = nav_y
heading_deg = heading

# ============================================================
# GAS FLARE DETECTION
# ============================================================

binary_flare = sv_db > FLARE_THRESHOLD_DB

binary_flare = binary_opening(
    binary_flare,
    structure=np.ones((1, VERTICAL_FILTER, 1))
)

labels, n_labels = label(binary_flare)

flare_results = []

# ============================================================
# ANALYZE EACH FLARE
# ============================================================

for lbl in range(1, n_labels + 1):

    component = labels == lbl

    for p in range(component.shape[0]):

        plume = component[p]
        if not plume.any():
            continue

        depth_idx = np.where(plume.any(axis=1))[0]
        beam_idx = np.where(plume.any(axis=0))[0]

        top = depth_idx.min()
        base = depth_idx.max()

        height_m = ranges_m[base] - ranges_m[top]
        if height_m < MIN_PLUME_HEIGHT_M:
            continue

        # Center beam
        beam_center = int(np.mean(beam_idx))
        beam_angle = np.deg2rad(beam_angles_deg[beam_center])

        # Horizontal distance from sonar
        range_center = ranges_m[base]
        x_offset = range_center * np.sin(beam_angle)
        y_offset = range_center * np.cos(beam_angle)

        # Rotate by vessel heading
        hdg = np.deg2rad(heading_deg[p])
        x_geo = x_ping[p] + x_offset * np.cos(hdg) - y_offset * np.sin(hdg)
        y_geo = y_ping[p] + x_offset * np.sin(hdg) + y_offset * np.cos(hdg)

        # Width estimation
        beam_width_rad = np.abs(
            np.deg2rad(beam_angles_deg[beam_idx[-1]] -
                       beam_angles_deg[beam_idx[0]])
        )
        plume_width_m = range_center * beam_width_rad

        flare_results.append({
            "ping": p,
            "x": round(x_geo, 2),
            "y": round(y_geo, 2),
            "height_m": round(height_m, 2),
            "width_m": round(plume_width_m, 2)
        })

# ============================================================
# WRITE TXT REPORT
# ============================================================

with open(TXT_OUTPUT, "w") as f:
    f.write("KONGSBERG MULTIBEAM GAS FLARE REPORT\n")
    f.write("=================================\n\n")

    for i, r in enumerate(flare_results, 1):
        f.write(f"Gas Flare #{i}\n")
        f.write(f"Ping        : {r['ping']}\n")
        f.write(f"X (meters)  : {r['x']}\n")
        f.write(f"Y (meters)  : {r['y']}\n")
        f.write(f"Height (m)  : {r['height_m']}\n")
        f.write(f"Width (m)   : {r['width_m']}\n")
        f.write("\n")

print(f"Gas flare report written to {TXT_OUTPUT}")
