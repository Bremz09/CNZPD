import json
from pathlib import Path

import pandas as pd


SYNC_SHEET_NAME = "FIT_Sync"
SYNC_REFERENCE_COLUMN = "FIT Sync File"
SYNC_DIRECTORY = Path("pages/video_analysis/FIT_Sync")


def parse_sync_bytes(sync_bytes):
    payload = json.loads(sync_bytes.decode("utf-8-sig"))
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
        raise ValueError("The sync file does not contain a valid files list.")

    rider_names = payload.get("riderNames", [])
    if not isinstance(rider_names, list):
        raise ValueError("The sync file does not contain valid rider names.")

    valid_files = []
    for fit_file in payload["files"]:
        if not isinstance(fit_file, dict) or not isinstance(fit_file.get("rows"), list):
            continue
        assigned_index = fit_file.get("assignedRiderIndex")
        if not isinstance(assigned_index, int) or not 0 <= assigned_index < len(rider_names):
            continue
        rows = [row for row in fit_file["rows"] if isinstance(row, dict) and row.get("Time") is not None]
        if not rows:
            continue
        valid_files.append({**fit_file, "assignedRiderIndex": assigned_index, "rows": rows})

    if not valid_files:
        raise ValueError("The sync file does not contain assigned FIT data rows.")

    return {
        "version": payload.get("version", 1),
        "createdAt": payload.get("createdAt", ""),
        "metricKey": payload.get("metricKey", ""),
        "riderNames": [str(name).strip() for name in rider_names],
        "files": valid_files,
    }


def attach_sync_reference(master_frame, session_title, sync_file_name):
    updated = master_frame.copy()
    if SYNC_REFERENCE_COLUMN not in updated.columns:
        updated[SYNC_REFERENCE_COLUMN] = ""
    session_text = str(session_title).strip()
    title_mask = updated["Title"].astype(str).str.strip() == session_text
    if not title_mask.any():
        raise ValueError(f"Session title not found in the master workbook: {session_text}")
    updated.loc[title_mask, SYNC_REFERENCE_COLUMN] = Path(str(sync_file_name)).name
    return updated


def load_sync_reference(sync_file_name, sync_directory=SYNC_DIRECTORY):
    file_name = Path(str(sync_file_name)).name
    if not file_name or file_name.lower() in {"nan", "none"}:
        return None
    sync_path = Path(sync_directory) / file_name
    if not sync_path.is_file():
        return None
    return parse_sync_bytes(sync_path.read_bytes())


def sync_payload_to_frame(session_title, payload):
    rows = []
    for fit_file in payload["files"]:
        rider_index = fit_file["assignedRiderIndex"]
        rider_name = payload["riderNames"][rider_index] if rider_index < len(payload["riderNames"]) else f"Rider {rider_index + 1}"
        fit_timestamps = [
            pd.to_numeric(sample.get("Time"), errors="coerce")
            for sample in fit_file["rows"]
        ]
        fit_timestamps = [float(timestamp) for timestamp in fit_timestamps if pd.notna(timestamp)]
        base_timestamp = min(fit_timestamps) if fit_timestamps else ""
        for chunk_index in range(0, len(fit_file["rows"]), 50):
            rows.append(
                {
                    "Session Title": str(session_title).strip(),
                    "Rider": rider_name,
                    "Rider Index": rider_index,
                    "File Name": str(fit_file.get("fileName", "")),
                    "Metric": str(payload.get("metricKey", "")),
                    "Offset (s)": fit_file.get("offset", 0),
                    "Sampling Hz": fit_file.get("samplingHz", ""),
                    "Base Time": base_timestamp,
                    "Chunk Index": chunk_index // 50,
                    "Rows JSON": json.dumps(fit_file["rows"][chunk_index:chunk_index + 50], separators=(",", ":")),
                }
            )
    return pd.DataFrame(rows)


def replace_session_sync(existing_frame, session_title, payload):
    new_frame = sync_payload_to_frame(session_title, payload)
    if existing_frame is None or existing_frame.empty:
        return new_frame
    session_text = str(session_title).strip()
    existing = existing_frame.copy()
    title_col = "Session Title"
    if title_col in existing.columns:
        existing = existing[existing[title_col].astype(str).str.strip() != session_text]
    return pd.concat([existing, new_frame], ignore_index=True)


def aligned_fit_frame(sync_frame, session_title, metric_key):
    if sync_frame is None or sync_frame.empty or "Session Title" not in sync_frame.columns:
        return pd.DataFrame()

    selected = sync_frame[
        sync_frame["Session Title"].astype(str).str.strip() == str(session_title).strip()
    ]
    points = []
    for _, record in selected.iterrows():
        try:
            samples = json.loads(record.get("Rows JSON", "[]"))
        except (TypeError, json.JSONDecodeError):
            continue
        samples = sorted(
            samples,
            key=lambda sample: pd.to_numeric(sample.get("Time"), errors="coerce"),
        )
        offset = pd.to_numeric(record.get("Offset (s)", 0), errors="coerce")
        offset = float(offset) if pd.notna(offset) else 0.0
        rider = str(record.get("Rider", "")).strip()
        base_timestamp = pd.to_numeric(record.get("Base Time"), errors="coerce")
        if pd.isna(base_timestamp):
            continue
        for sample in samples:
            timestamp = pd.to_numeric(sample.get("Time"), errors="coerce")
            value = pd.to_numeric(sample.get(metric_key), errors="coerce")
            if pd.notna(timestamp) and pd.notna(value):
                points.append(
                    {
                        "Video Time (s)": float(timestamp) - base_timestamp + offset,
                        "Value": float(value),
                        "Rider": rider,
                    }
                )
    return pd.DataFrame(points).sort_values("Video Time (s)").reset_index(drop=True) if points else pd.DataFrame()