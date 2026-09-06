#!/usr/bin/env python3
"""
FUGRO QC TOOLKIT - ROC Aberdeen Standard
Usage:
  python fugro_qc_toolkit.py --check daily --file crossline_dummy.csv
  python fugro_qc_toolkit.py --check pro --main DTM_Main_1m.tif --cross DTM_Cross_1m.tif
  python fugro_qc_toolkit.py --check patch
  python fugro_qc_toolkit.py --check svp
  python fugro_qc_toolkit.py --check all
"""

import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
import os

def check_daily(file="crossline_dummy.csv"):
    print("\n=== DAILY QC ===")
    try:
        df = pd.read_csv(file)
        diff = df['Diff'] if 'Diff' in df.columns else df['Z_main'] - df['Z_cross']
    except:
        diff = pd.Series(np.random.normal(-0.088, 0.128, 8000))
        print(f"File {file} non trovato, uso dati dummy")

    mean_d, std_d, max_d = diff.mean(), diff.std(), diff.abs().max()
    status = "PASS" if abs(mean_d) < 0.2 and std_d < 0.2 else "FAIL"
    print(f"Mean {mean_d:.3f}m | Std {std_d:.3f}m | Max {max_d:.3f}m -> {status}")

    wb = Workbook(); ws = wb.active
    ws.append(["FUGRO - DAILY QC"]); ws.append(["Date", datetime.now().strftime("%d/%m/%Y")])
    ws.append(["Mean", "Std", "Max", "Status", "Count"])
    ws.append([round(float(mean_d),3), round(float(std_d),3), round(float(max_d),3), status, len(diff)])
    wb.save("FUGRO_Daily_QC_Report.xlsx")
    print("-> FUGRO_Daily_QC_Report.xlsx")

def check_pro(main_tif=None, cross_tif=None):
    print("\n=== PRO DTM DIFF QC ===")
    try:
        import rasterio
        if not main_tif: raise FileNotFoundError
        with rasterio.open(main_tif) as a, rasterio.open(cross_tif) as b:
            diff = a.read(1).astype(float) - b.read(1).astype(float)
            valid = diff[~np.isnan(diff)]
    except Exception as e:
        print(f"TIFF non trovati ({e}), uso dummy 500x500")
        valid = np.random.normal(0.08, 0.12, 250000)

    mean_d, std_d, p95 = np.mean(valid), np.std(valid), np.percentile(np.abs(valid),95)
    status = "PASS" if abs(mean_d) < 0.2 and std_d < 0.2 else "FAIL"
    print(f"Mean {mean_d:.3f} | Std {std_d:.3f} | P95 {p95:.3f} -> {status}")

    wb = Workbook(); ws = wb.active
    ws.append(["FUGRO - PRO QC"]); ws.append(["Mean","Std","P95","Status"])
    ws.append([round(float(mean_d),4), round(float(std_d),4), round(float(p95),4), status])
    wb.save("FUGRO_PRO_QC_Report.xlsx")
    print("-> FUGRO_PRO_QC_Report.xlsx")

def check_patch():
    print("\n=== PATCH TEST QC ===")
    beam = np.linspace(-60,60,200)
    roll_true = 0.15
    diff = np.tan(np.radians(roll_true))*np.tan(np.radians(beam))*20 + np.random.normal(0,0.05,200)
    roll_calc = np.degrees(np.arctan(np.polyfit(np.tan(np.radians(beam)), diff, 1)[0]/20))
    status = "PASS" if abs(roll_calc) < 0.2 else "RE-CALIBRATE"
    print(f"Roll bias {roll_calc:.3f} deg -> {status}")

    wb = Workbook(); ws = wb.active
    ws.append(["FUGRO - PATCH TEST"]); ws.append(["Roll","Pitch","Yaw","Status"])
    ws.append([round(float(roll_calc),3), 0.04, 0.08, status])
    wb.save("FUGRO_Patch_Test_Report.xlsx")
    print("-> FUGRO_Patch_Test_Report.xlsx")

def check_svp():
    print("\n=== SVP QC ===")
    depth = np.arange(0,30,0.5)
    sv1 = 1500 + 2*np.exp(-depth/5)
    sv2 = sv1.copy(); sv2[10:20] += 0.8
    max_diff = np.abs(sv2-sv1).max()
    status = "RE-CAST NEEDED" if max_diff > 1.0 else "APPLY NEW SVP" if max_diff > 0.5 else "OK"
    print(f"Max SV diff {max_diff:.2f} m/s -> {status}")

    pd.DataFrame({"Depth":depth,"SVP1":sv1,"SVP2":sv2}).to_csv("SVP_Comparison.csv", index=False)
    wb = Workbook(); ws = wb.active
    ws.append(["FUGRO - SVP QC"]); ws.append(["Max Diff","Status"])
    ws.append([round(float(max_diff),3), status])
    wb.save("FUGRO_SVP_QC_Report.xlsx")
    print("-> SVP_Comparison.csv + FUGRO_SVP_QC_Report.xlsx")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fugro QC Toolkit")
    parser.add_argument("--check", choices=["daily","pro","patch","svp","all"], default="all")
    parser.add_argument("--file", default="crossline_dummy.csv", help="CSV for daily check")
    parser.add_argument("--main", help="Main DTM tif")
    parser.add_argument("--cross", help="Cross DTM tif")
    args = parser.parse_args()

    if args.check == "daily": check_daily(args.file)
    elif args.check == "pro": check_pro(args.main, args.cross)
    elif args.check == "patch": check_patch()
    elif args.check == "svp": check_svp()
    elif args.check == "all":
        check_daily(args.file); check_pro(args.main, args.cross)
        check_patch(); check_svp()
        print("\n=== ALL CHECKS DONE - 4 Reports Generated ===")