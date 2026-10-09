#!/usr/bin/env python3
"""Tổng hợp host, storage và network/VLAN của cluster Proxmox ra màn hình và CSV."""

import csv
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path(f"proxmox-inventory-{datetime.now():%Y%m%d-%H%M%S}")
MEMBERS_FILE = Path("/etc/pve/.members")


def pvesh_json(path: str) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["pvesh", "get", path, "--output-format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return data if isinstance(data, list) else []


def get_value(data: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        for candidate in (key, key.replace("-", "_"), key.replace("_", "-")):
            if candidate in data and data[candidate] is not None:
                return data[candidate]
    return default


def is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled"}


def display_value(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return str(value).replace("\n", ", ").replace("\r", "")


def human_bytes(value: Any) -> str:
    if value is None or value == "":
        return "-"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)

    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    unit_index = 0
    while amount >= 1024 and unit_index < len(units) - 1:
        amount /= 1024
        unit_index += 1
    return f"{amount:.2f} {units[unit_index]}"


def format_percent(value: Any) -> str:
    if value is None or value == "":
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if 0 <= number <= 1:
        number *= 100
    return f"{number:.1f}%"


def print_table(
    title: str,
    columns: list[tuple[str, str]],
    rows: list[dict[str, Any]],
) -> None:
    print(f"\n{title}")
    if not rows:
        print("(Không có dữ liệu)")
        return

    headers = [label for _, label in columns]
    values = [
        [display_value(row.get(key, "")) for key, _ in columns]
        for row in rows
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in values))
        for index in range(len(headers))
    ]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(border)
    print("| " + " | ".join(
        headers[index].ljust(widths[index]) for index in range(len(headers))
    ) + " |")
    print(border)
    for row in values:
        print("| " + " | ".join(
            row[index].ljust(widths[index]) for index in range(len(row))
        ) + " |")
    print(border)


def write_csv(filename: str, rows: list[dict[str, Any]], fields: list[str]) -> None:
    filepath = OUTPUT_DIR / filename
    with filepath.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def error_message(exc: Exception) -> str:
    if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
        return exc.stderr.strip()
    return str(exc).strip()


def load_hosts() -> list[dict[str, Any]]:
    if not MEMBERS_FILE.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy {MEMBERS_FILE}. "
            "Hãy chạy script trên một node thuộc cluster Proxmox."
        )

    with MEMBERS_FILE.open(encoding="utf-8") as file:
        members = json.load(file)

    hosts = []
    nodelist = members.get("nodelist", {})
    for hostname, info in sorted(
        nodelist.items(),
        key=lambda item: (item[1].get("id", 0), item[0]),
    ):
        online = info.get("online", "")
        if str(online).strip().lower() in {"1", "true"}:
            online_text = "Online"
        elif str(online).strip().lower() in {"0", "false"}:
            online_text = "Offline"
        else:
            online_text = online

        hosts.append({
            "hostname": hostname,
            "nodeid": info.get("id", ""),
            "membership_ip": (
                info.get("ip")
                or info.get("ring0_addr")
                or info.get("ring1_addr")
                or ""
            ),
            "online": online_text,
        })
    return hosts


def load_cluster_storages() -> list[dict[str, Any]]:
    storages = pvesh_json("/storage")
    for storage in storages:
        storage["storage"] = (
            storage.get("storage")
            or storage.get("name")
            or storage.get("id")
            or ""
        )
        storage["enabled"] = not is_true(storage.get("disable", False))
    return storages


def load_storage_status(
    hosts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for host in hosts:
        hostname = host["hostname"]
        try:
            for item in pvesh_json(f"/nodes/{hostname}/storage"):
                total = item.get("total", "")
                used = item.get("used", "")
                available = item.get("avail", item.get("available", ""))
                rows.append({
                    "hostname": hostname,
                    "storage": item.get("storage", ""),
                    "type": item.get("type", ""),
                    "active": item.get("active", ""),
                    "enabled": item.get("enabled", ""),
                    "total": total,
                    "used": used,
                    "available": available,
                    "total_readable": human_bytes(total),
                    "used_readable": human_bytes(used),
                    "available_readable": human_bytes(available),
                    "used_percent": format_percent(
                        item.get("used_fraction", "")
                    ),
                    "error": "",
                })
        except (subprocess.CalledProcessError, OSError, json.JSONDecodeError) as exc:
            rows.append({"hostname": hostname, "error": error_message(exc)})
    return rows


def extract_vlan_id(interface: str) -> str:
    match = re.search(r"\.(\d+)$", interface)
    if match:
        return match.group(1)
    match = re.fullmatch(r"vlan(\d+)", interface, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def get_interface_address(item: dict[str, Any]) -> Any:
    cidr = get_value(item, "cidr")
    if cidr:
        return cidr
    address = get_value(item, "address")
    netmask = get_value(item, "netmask")
    if address and netmask:
        return f"{address}/{netmask}"
    return address


def load_networks(
    hosts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    network_rows = []
    summary_rows = []
    for host in hosts:
        hostname = host["hostname"]
        vlan_ids: set[str] = set()
        vlan_interface_count = 0
        vlan_aware_bridge_count = 0
        error = ""
        try:
            interfaces = pvesh_json(f"/nodes/{hostname}/network")
            for item in interfaces:
                interface = str(get_value(item, "iface"))
                interface_type = str(get_value(item, "type")).lower()
                vlan_id = get_value(item, "vlan-id")
                if vlan_id == "":
                    vlan_id = extract_vlan_id(interface)

                is_vlan_interface = (
                    interface_type == "vlan" or vlan_id not in ("", None)
                )
                is_bridge = interface_type in {"bridge", "ovsbridge", "ovs-bridge"}
                vlan_aware = is_bridge and is_true(
                    get_value(item, "bridge-vlan-aware", default=False)
                )
                if not is_vlan_interface and not vlan_aware:
                    continue

                if is_vlan_interface:
                    vlan_interface_count += 1
                    if vlan_id not in ("", None):
                        vlan_ids.add(str(vlan_id))
                if vlan_aware:
                    vlan_aware_bridge_count += 1

                if is_vlan_interface and vlan_aware:
                    network_type = "VLAN interface + VLAN-aware bridge"
                elif is_vlan_interface:
                    network_type = "VLAN interface"
                else:
                    network_type = "VLAN-aware bridge"
                network_rows.append({
                    "hostname": hostname,
                    "interface": interface,
                    "network_type": network_type,
                    "vlan_id": vlan_id,
                    "vlan_ranges": get_value(item, "bridge-vids"),
                    "vlan_raw_device": get_value(item, "vlan-raw-device"),
                    "bridge_ports": get_value(item, "bridge-ports"),
                    "address": get_interface_address(item),
                    "gateway": get_value(item, "gateway"),
                    "active": get_value(item, "active"),
                    "autostart": get_value(item, "autostart"),
                    "comments": get_value(item, "comments"),
                })
        except (subprocess.CalledProcessError, OSError, json.JSONDecodeError) as exc:
            error = error_message(exc)

        summary_rows.append({
            "hostname": hostname,
            "vlan_interface_count": vlan_interface_count,
            "unique_vlan_id_count": len(vlan_ids),
            "vlan_aware_bridge_count": vlan_aware_bridge_count,
            "error": error,
        })
    return network_rows, summary_rows


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hosts = load_hosts()
    storages = load_cluster_storages()
    storage_status = load_storage_status(hosts)
    network_rows, network_summary = load_networks(hosts)

    print_table(
        "1. HOST TRONG CLUSTER",
        [
            ("hostname", "Hostname"),
            ("nodeid", "Node ID"),
            ("membership_ip", "IP trong .members"),
            ("online", "Trạng thái"),
        ],
        hosts,
    )
    print_table(
        "2. DATASTORE KHAI BÁO TRONG CLUSTER",
        [
            ("storage", "Datastore"),
            ("type", "Loại"),
            ("content", "Content"),
            ("shared", "Shared"),
            ("enabled", "Đang bật"),
            ("nodes", "Node áp dụng"),
        ],
        storages,
    )
    print_table(
        "3. TRẠNG THÁI DATASTORE THEO HOST",
        [
            ("hostname", "Hostname"),
            ("storage", "Datastore"),
            ("type", "Loại"),
            ("active", "Active"),
            ("enabled", "Enabled"),
            ("total_readable", "Tổng dung lượng"),
            ("used_readable", "Đã dùng"),
            ("available_readable", "Còn trống"),
            ("used_percent", "Đã dùng (%)"),
            ("error", "Lỗi"),
        ],
        storage_status,
    )
    print_table(
        "4. TỔNG HỢP VLAN THEO HOST",
        [
            ("hostname", "Hostname"),
            ("vlan_interface_count", "Số VLAN interface"),
            ("unique_vlan_id_count", "Số VLAN ID khác nhau"),
            ("vlan_aware_bridge_count", "Số bridge VLAN-aware"),
            ("error", "Lỗi"),
        ],
        network_summary,
    )
    for host in hosts:
        hostname = host["hostname"]
        host_networks = [
            row for row in network_rows if row["hostname"] == hostname
        ]
        print_table(
            f"5. NETWORK/VLAN CỦA HOST {hostname}",
            [
                ("interface", "Interface"),
                ("network_type", "Loại network"),
                ("vlan_id", "VLAN ID"),
                ("vlan_ranges", "VLAN ranges"),
                ("vlan_raw_device", "VLAN raw device"),
                ("bridge_ports", "Bridge ports"),
                ("address", "IP/Subnet"),
                ("gateway", "Gateway"),
                ("active", "Active"),
                ("autostart", "Autostart"),
                ("comments", "Ghi chú"),
            ],
            host_networks,
        )

    write_csv("hosts.csv", hosts, [
        "hostname", "nodeid", "membership_ip", "online",
    ])
    write_csv("storage.csv", storages, [
        "storage", "type", "content", "shared", "disable", "enabled", "nodes",
    ])
    write_csv("storage-status-by-host.csv", storage_status, [
        "hostname", "storage", "type", "active", "enabled",
        "total", "used", "available", "total_readable", "used_readable",
        "available_readable", "used_percent", "error",
    ])
    write_csv("network-summary-by-host.csv", network_summary, [
        "hostname", "vlan_interface_count", "unique_vlan_id_count",
        "vlan_aware_bridge_count", "error",
    ])
    write_csv("networks-by-host.csv", network_rows, [
        "hostname", "interface", "network_type", "vlan_id", "vlan_ranges",
        "vlan_raw_device", "bridge_ports", "address", "gateway", "active",
        "autostart", "comments",
    ])

    enabled_storage_count = sum(
        1 for storage in storages if storage.get("enabled")
    )
    print("\nTỔNG KẾT")
    print(f"Số host trong .members: {len(hosts)}")
    print(
        f"Số datastore khai báo: {len(storages)} "
        f"(đang bật: {enabled_storage_count})"
    )
    print(f"Số dòng network/VLAN thu thập được: {len(network_rows)}")
    print(f"Các file CSV đã lưu tại: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (subprocess.CalledProcessError, OSError, json.JSONDecodeError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else ""
        print(f"Script gặp lỗi: {detail or exc}")
        raise SystemExit(1) from exc
