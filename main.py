import os
import sys
import json
import random

import benchmark
import fetch_servers

from rich import print


def select_continent() -> list[str]:
    continents = json.load(open("servers/continents.json"))
    for i, continent in enumerate(continents):
        print(f"[green]{i + 1}. {continent}[/green]")

    print()
    print("[magenta]Select a continent by number:[/magenta]")
    selected = int(input(">>> ")) - 1
    if selected < 0 or selected >= len(continents):
        print("[red]Invalid selection. Exiting.[/red]")
        sys.exit(1)

    selected_continent = list(continents.keys())[selected]

    print(f"You selected: [blue]{selected_continent}[/blue]")

    return continents[selected_continent]


def setup():
    if os.path.exists("config.json"):
        config = json.load(open("config.json"))

        print("[bold green]Config ready![/bold green]")
        print(f"[blue]{len(config['regions'])} regions[/blue]")
        print(f"[blue]{config['servers_per_region']} servers per region[/blue]")

        return config

    regions = select_continent()
    print(f"[blue]Regions:[/blue] {', '.join(regions)}")

    print("\n[magenta]How many servers per region? (recommended: 3)[/magenta]")
    servers_per_region = int(input(">>> "))

    if servers_per_region <= 0:
        print("[red]Invalid number. Exiting.[/red]")
        sys.exit(1)

    config = {
        "regions": regions,
        "servers_per_region": servers_per_region,
    }

    open("config.json", "w").write(json.dumps(config, indent=4))

    return config


def main():
    config = setup()
    servers = fetch_servers.fetch_server_data()

    servers = {
        region: random.sample(ips, min(len(ips), config["servers_per_region"]))
        for region, ips in servers.items()
        if region in config["regions"]
    }

    print(
        f"\n[bold green]{sum(len(v) for v in servers.values())} Servers available[/bold green]"
    )

    print(servers)

    res = benchmark.benchmark_latencies(servers)
    print("\n[bold green]Benchmark Results (latency in ms):[/bold green]")
    # sort by latency, low to high
    res = dict(sorted(res.items(), key=lambda item: (item[1] is None, item[1])))
    print(res)

    open("results.json", "w").write(json.dumps(res, indent=4))


main()
