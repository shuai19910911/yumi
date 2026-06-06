#!/usr/bin/env python3
"""Download a large HTTP resource with Range requests and resumable chunks."""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--chunk-size", type=int, default=32 * 1024 * 1024)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--proxy", default="")
    parser.add_argument("--curl", default="curl")
    return parser.parse_args()


def run_chunk(args: argparse.Namespace, idx: int, start: int, end: int, chunks_dir: Path) -> tuple[int, str]:
    expected = end - start + 1
    final = chunks_dir / f"chunk_{idx:05d}.part"
    tmp = chunks_dir / f"chunk_{idx:05d}.tmp"
    if final.exists() and final.stat().st_size == expected:
        return idx, "exists"
    cmd = [
        args.curl,
        "-fL",
        "--max-time",
        "1200",
        "-r",
        f"{start}-{end}",
        args.url,
        "-o",
        str(tmp),
    ]
    if args.proxy:
        cmd[1:1] = ["-x", args.proxy]
    last_status = ""
    for attempt in range(1, args.attempts + 1):
        if tmp.exists():
            tmp.unlink()
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode != 0:
            last_status = f"failed:{result.returncode}:attempt{attempt}"
            time.sleep(min(30, 2 * attempt))
            continue
        size = tmp.stat().st_size
        if size != expected:
            tmp.unlink()
            last_status = f"bad_size:{size}!={expected}:attempt{attempt}"
            time.sleep(min(30, 2 * attempt))
            continue
        tmp.replace(final)
        return idx, "downloaded" if attempt == 1 else f"downloaded_after_{attempt}"
    return idx, last_status or "failed"


def concatenate(chunks: list[Path], out: Path, expected_size: int) -> None:
    tmp_out = out.with_suffix(out.suffix + ".tmp")
    if tmp_out.exists():
        tmp_out.unlink()
    with tmp_out.open("wb") as writer:
        for chunk in chunks:
            with chunk.open("rb") as reader:
                while True:
                    data = reader.read(8 * 1024 * 1024)
                    if not data:
                        break
                    writer.write(data)
    if tmp_out.stat().st_size != expected_size:
        raise SystemExit(f"Concatenated size mismatch: {tmp_out.stat().st_size} != {expected_size}")
    tmp_out.replace(out)


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    chunks_dir = out.with_name(out.name + ".chunks")
    chunks_dir.mkdir(parents=True, exist_ok=True)
    n_chunks = math.ceil(args.size / args.chunk_size)
    ranges = []
    for idx in range(n_chunks):
        start = idx * args.chunk_size
        end = min(args.size - 1, start + args.chunk_size - 1)
        ranges.append((idx, start, end))

    completed = 0
    failures: list[tuple[int, str]] = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run_chunk, args, idx, start, end, chunks_dir) for idx, start, end in ranges]
        for future in as_completed(futures):
            idx, status = future.result()
            completed += 1
            print({"chunk": idx, "status": status, "completed": completed, "total": n_chunks}, flush=True)
            if status.startswith("failed") or status.startswith("bad_size"):
                failures.append((idx, status))
    if failures:
        raise SystemExit(f"Failed chunks remain; rerun to resume: {failures[:10]}")

    chunk_paths = [chunks_dir / f"chunk_{idx:05d}.part" for idx in range(n_chunks)]
    missing = [str(p) for p in chunk_paths if not p.exists()]
    if missing:
        raise SystemExit(f"Missing chunks: {missing[:5]}")
    concatenate(chunk_paths, out, args.size)
    print({"out": str(out), "size": out.stat().st_size, "chunks": n_chunks}, flush=True)


if __name__ == "__main__":
    main()
