import calendar
from collections import defaultdict
from datetime import datetime

from app.libs import load_cached_data
from app.models import AnalyticsResponse, ChartData, Launch, Rocket


def rocket_success_rate(launches: list[Launch], rockets: list[Rocket]) -> ChartData:
    rocket_names = {r.id: r.name for r in rockets}

    stats: dict[str, list[int]] = {}

    for launch in launches:
        name = rocket_names.get(launch.rocket, launch.rocket)
        stats.setdefault(name, []).append(1 if launch.success else 0)

    labels = list(stats.keys())
    values = [sum(v) / len(v) for v in stats.values()]

    return {"labels": labels, "values": values}


def launches_by_site(launches: list[Launch]) -> ChartData:
    sites = {}

    for item in launches:
        sites.setdefault(item.launchpad, 0)
        sites[item.launchpad] += 1

    labels = list(sites.keys())
    values = list(sites.values())

    return {"labels": labels, "values": values}


def launch_frequency(launches: list[Launch]) -> ChartData:
    freq = defaultdict(lambda: {m: 0 for m in calendar.month_name[1:]})

    for item in launches:
        t = item.date_unix
        dt = datetime.utcfromtimestamp(t)
        freq[dt.year][calendar.month_name[dt.month]] += 1

    labels = list(freq.keys())
    values = [list(freq[year].values()) for year in labels]

    return {"labels": labels, "values": values}


async def analytics(request) -> AnalyticsResponse:
    data = await load_cached_data(request)
    rate = rocket_success_rate(data["launches"], data["rockets"])
    site_launches = launches_by_site(data["launches"])
    lf = launch_frequency(data["launches"])
    return {
        "successByRocket": rate,
        "launchesBySite": site_launches,
        "frequencyByYear": lf,
    }
