# Fugro QC Toolkit - Offshore Survey QC Automation

Python toolkit for automated QC of Multibeam Echosounder (MBES) data following Fugro ROC Aberdeen standards. Developed for offshore wind farm surveys and hydrographic operations.

## Features

- **Daily QC** - Cross-line difference analysis (Mean / Std / Max) with PASS/FAIL against IHO S-44 / Fugro 20cm tolerance
- **PRO DTM Diff** - Raster-based DTM difference using `rasterio` (1m grid), 95th percentile, diff GeoTIFF export
- **Patch Test** - Roll / Pitch / Yaw bias estimation from reciprocal lines
- **SVP Check** - Sound Velocity Profile comparison, thermocline detection, re-cast decision logic

## Fugro Standards Implemented

- Tolerance: 0.20 m for cross-line mean & std dev
- SVP re-cast threshold: >1.0 m/s difference, reprocess threshold >0.5 m/s
- Patch test tolerance: <0.2 deg roll
- Deliverables: `*.xlsx` Daily Report + `DIFF.tif` + `QC histogram`

## Installation

```bash
pip install -r requirements.txt