import httpx
import pandas as pd

from rich import print

SERVER_CSV_DOWNLOAD = (
    "https://raw.githubusercontent.com/Lars-/PIA-servers/refs/heads/master/export.csv"
)


def fetch_server_data() -> dict:
    # response = httpx.get(SERVER_CSV_DOWNLOAD)
    # response.raise_for_status()

    # open("servers/export.csv", "wb").write(response.content)

    df = pd.read_csv(
        "servers/export.csv", engine="c", low_memory=False
    )  # IP,Region,LastSeenTimestamp

    regions = df["Region"].unique().tolist()
    print(f"[green]Fetched {len(regions)} regions from {SERVER_CSV_DOWNLOAD}[/green]")

    open("servers/regions.txt", "w").write(
        "\n".join(regions)
    )  # not used currently, but useful

    region_to_ips = {}
    for region in regions:
        ips = df[df["Region"] == region]["IP"].tolist()
        region_to_ips[region] = ips

    return region_to_ips


if __name__ == "__main__":
    data = fetch_server_data(SERVER_CSV_DOWNLOAD)
