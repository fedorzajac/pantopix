import csv
import json
from io import StringIO
from typing import List

from fastapi.responses import StreamingResponse

from app.models import Launch


def export_to_csv(launches: List[Launch]) -> StreamingResponse:
    """
    Export to CSV format.
    """
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "name",
            "date_utc",
            "date_unix",
            "rocket",
            "launchpad",
            "success",
            "details",
        ],
    )

    writer.writeheader()
    for launch in launches:
        writer.writerow(
            {
                "id": launch.id,
                "name": launch.name,
                "date_utc": launch.date_utc,
                "date_unix": launch.date_unix,
                "rocket": launch.rocket,
                "launchpad": launch.launchpad,
                "success": launch.success,
                "details": launch.details or "",
            }
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=launches.csv"},
    )


def export_to_json(launches: List[Launch]) -> StreamingResponse:
    """Export launches to JSON format."""
    data = [launch.model_dump() for launch in launches]

    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=launches.json"},
    )
