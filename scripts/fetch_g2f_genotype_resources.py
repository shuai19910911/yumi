#!/usr/bin/env python3
"""Resolve and optionally download G2F 2014-2023 maize genotype resources.

The CyVerse CKAN API is reachable even when anonymous file downloads are
temporarily blocked by the CyVerse IP verification page. This script always
writes a machine-readable manifest from CKAN metadata, then optionally attempts
to download the listed files.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


CKAN_PACKAGE_URL = (
    "https://dc.cyverse.org/api/3/action/package_show"
    "?id=genomes_to_fields_genotypic_data_from_2014_to_2023"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="data/external/g2f/genotypic_2014_2023")
    parser.add_argument("--manifest", default="data/external/g2f/genotypic_2014_2023/resource_manifest.tsv")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--chunk-size", type=int, default=1024 * 1024)
    return parser.parse_args()


def fetch_json(url: str, timeout: int) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "yumi-g2f-ingest/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as handle:  # noqa: S310 - fixed public HTTPS URL.
        return json.loads(handle.read().decode("utf-8"))


def write_manifest(package: dict, out_path: Path) -> list[dict]:
    result = package["result"]
    rows = []
    for resource in result["resources"]:
        rows.append(
            {
                "dataset": result["title"],
                "citation": next(
                    (x["value"] for x in result.get("extras", []) if x.get("key", "").lower() == "citation"),
                    "",
                ),
                "license": result.get("license_title", ""),
                "metadata_created": result.get("metadata_created", ""),
                "metadata_modified": result.get("metadata_modified", ""),
                "resource_name": resource["name"],
                "format": resource.get("format", ""),
                "url": resource["url"],
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    keys = ["dataset", "citation", "license", "metadata_created", "metadata_modified", "resource_name", "format", "url"]
    with out_path.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(keys) + "\n")
        for row in rows:
            handle.write("\t".join(str(row.get(k, "")) for k in keys) + "\n")
    return rows


def looks_like_verification_page(path: Path) -> bool:
    if path.stat().st_size > 2_000_000:
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")[:50_000].lower()
    return "ip verification required" in text or "unblock me" in text or "turnstile" in text


def download_resource(row: dict, out_dir: Path, timeout: int, chunk_size: int) -> dict:
    url = row["url"]
    out_path = out_dir / row["resource_name"]
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "yumi-g2f-ingest/0.1"})
    out_dir.mkdir(parents=True, exist_ok=True)
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
        return {
            "resource_name": row["resource_name"],
            "path": str(out_path),
            "size_bytes": out_path.stat().st_size,
            "status": "blocked_by_cyverse_ip_verification" if blocked else "downloaded",
        }
    except urllib.error.HTTPError as exc:
        return {"resource_name": row["resource_name"], "path": str(out_path), "status": f"http_error_{exc.code}"}
    except urllib.error.URLError as exc:
        return {"resource_name": row["resource_name"], "path": str(out_path), "status": f"url_error_{exc.reason}"}


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    manifest = Path(args.manifest)
    package = fetch_json(CKAN_PACKAGE_URL, args.timeout)
    if not package.get("success"):
        raise SystemExit(f"CKAN package lookup failed: {package}")
    rows = write_manifest(package, manifest)

    result = {
        "ckan_package_url": CKAN_PACKAGE_URL,
        "manifest": str(manifest),
        "n_resources": len(rows),
        "resources": rows,
        "downloads": [],
    }
    if args.download:
        for row in rows:
            result["downloads"].append(download_resource(row, out_dir, args.timeout, args.chunk_size))

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if any(item.get("status") == "blocked_by_cyverse_ip_verification" for item in result["downloads"]):
        print(
            "CyVerse returned its IP verification page instead of data. "
            "Open one data.cyverse.org resource URL in a browser from this network and complete verification, "
            "or rerun from a different permitted node.",
            file=sys.stderr,
        )
        raise SystemExit(2)


if __name__ == "__main__":
    main()
