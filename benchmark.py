from __future__ import annotations
from statistics import median, mean
from typing import Dict, List, Iterable, Optional
from icmplib import multiping, Host


def _aggregate(vals: Iterable[Optional[float]], agg: str) -> Optional[float]:
    cleaned = [v for v in vals if v is not None]
    if not cleaned:
        return None
    if agg == "mean":
        return float(mean(cleaned))
    return float(median(cleaned))


def _per_host_stat(h: Host, per_host: str) -> Optional[float]:
    if h.packets_received == 0:
        return None
    if per_host == "min":
        return float(h.min_rtt)
    if per_host == "max":
        return float(h.max_rtt)
    if per_host == "median":
        return float(median([r for r in (h.rtts or []) if r is not None]) or h.avg_rtt)
    return float(h.avg_rtt)


def benchmark_latencies(
    regions_to_servers: Dict[str, List[str]],
    *,
    count: int = 3,
    interval: float = 0.20,
    timeout: float = 1.0,
    privileged: bool = False,
    agg: str = "median",
    per_host: str = "avg",
    batch_size: Optional[int] = None,
) -> Dict[str, Optional[float]]:
    ip_to_region: Dict[str, str] = {}
    all_ips: List[str] = []
    for region, ips in regions_to_servers.items():
        for ip in ips:
            ip_to_region[ip] = region
            all_ips.append(ip)
    if not all_ips:
        return {}
    per_region_values: Dict[str, List[Optional[float]]] = {
        r: [] for r in regions_to_servers
    }
    if batch_size is None or batch_size <= 0:
        batch_size = len(all_ips)
    for start in range(0, len(all_ips), batch_size):
        batch = all_ips[start : start + batch_size]
        hosts: List[Host] = multiping(
            batch,
            count=count,
            interval=interval,
            timeout=timeout,
            privileged=privileged,
        )
        for h in hosts:
            stat = _per_host_stat(h, per_host)
            per_region_values[ip_to_region[h.address]].append(stat)
    return {region: _aggregate(vals, agg) for region, vals in per_region_values.items()}
