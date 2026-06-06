#!/usr/bin/env python3
"""Optionally download Panzea HapMap3.2.1 AGPv4 chromosome VCF files."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = (
    "https://data.cyverse.org/dav-anon/iplant/home/shared/panzea/"
    "hapmap3/hmp321/unimputed/uplifted_APGv4"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data/external/panzea/hapmap3/hmp321_agpv4")
    parser.add_argument("--manifest", default="data/external/panzea/hapmap3/hmp321_agpv4/resource_manifest.tsv")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    return parser.parse_args()


def resources() -> list[dict[str, str]]:
    rows = []
    for chrom in range(1, 11):
        name = f"hmp321_agpv4_chr{chrom}.vcf.gz"
        rows.append(
            {
                "dataset": "Panzea HapMap3.2.1 AGPv4 unimputed",
                "resource_name": name,
                "format": "vcf.gz",
                "url": f"{BASE_URL}/{name}",
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = ["dataset", "resource_name", "format", "url"]
    with path.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(keys) + "\n")
        for row in rows:
            handle.write("\t".join(row[k] for k in keys) + "\n")


def looks_like_verification_page(path: Path) -> bool:
    if path.stat().st_size > 2_000_000:
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")[:50_000].lower()
    return "ip verification required" in text or "unblock me" in text or "turnstile" in text


def download(row: dict[str, str], out_dir: Path, timeout: int, chunk_size: int) -> dict[str, object]:
    out_path = out_dir / row["resource_name"]
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")
    request = urllib.request.Request(row["url"], headers={"User-Agent": "yumi-panzea-ingest/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed public HTTPS URL.
            with tmp_path.open("wb") as handle:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    handle.write(chunk)
        tmp_path.replace(out_path)
        blocked = looks_like_verification_page(out_path)
        blocked_path = ""
        size_bytes = out_path.stat().st_size
        if blocked:
            blocked_path = str(out_path.with_name(out_path.name + ".blocked.html"))
            out_path.replace(blocked_path)
            size_bytes = Path(blocked_path).stat().st_size
        return {
            "resource_name": row["resource_name"],
            "path": str(out_path),
            "size_bytes": size_bytes,
            "status": "blocked_by_cyverse_ip_verification" if blocked else "downloaded",
            "blocked_page_path": blocked_path,
        }
    except urllib.error.HTTPError as exc:
        return {"resource_name": row["resource_name"], "path": str(out_path), "status": f"http_error_{exc.code}"}
    except urllib.error.URLError as exc:
        return {"resource_name": row["resource_name"], "path": str(out_path), "status": f"url_error_{exc.reason}"}


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    manifest = Path(args.manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = resources()
    write_manifest(rows, manifest)
    result = {"base_url": BASE_URL, "manifest": str(manifest), "n_resources": len(rows), "downloads": []}
    if args.download:
        for row in rows:
            result["downloads"].append(download(row, out_dir, args.timeout, args.chunk_size))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if any(item.get("status") == "blocked_by_cyverse_ip_verification" for item in result["downloads"]):
        print(
            "CyVerse returned its IP verification page instead of Panzea data.",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
