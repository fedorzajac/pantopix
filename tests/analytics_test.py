from datetime import datetime

from app.analytics import launch_frequency, launches_by_site, rocket_success_rate
from app.models import Launch, Rocket

launches = [
    Launch(
        id="cached",
        name="Cached Launch",
        date_utc="2020-01-01T00:00:00Z",
        date_unix=datetime(2020, 1, 1).timestamp(),
        rocket="rocket1",
        launchpad="A",
        success=True,
        details=None,
        links={},
    ),
    Launch(
        id="cached",
        name="Cached Launch",
        date_utc="2020-01-01T00:00:00Z",
        date_unix=datetime(2020, 1, 14).timestamp(),
        rocket="rocket2",
        launchpad="A",
        success=True,
        details=None,
        links={},
    ),
    Launch(
        id="cached",
        name="Cached Launch",
        date_utc="2020-01-01T00:00:00Z",
        date_unix=datetime(2021, 3, 25).timestamp(),
        rocket="rocket2",
        launchpad="B",
        success=False,
        details=None,
        links={},
    ),
]

rockets = [
    Rocket(id="rocket1", name="rocket1_name"),
    Rocket(id="rocket2", name="rocket2_name"),
]


def test_rocket_success_rate_basic():
    result = rocket_success_rate(launches, rockets)

    assert result["labels"] == ["rocket1_name", "rocket2_name"]
    assert result["values"][0] == 1
    assert result["values"][1] == 0.5


from app.analytics import launches_by_site


def test_launches_by_site_counts():
    result = launches_by_site(launches)

    assert result["labels"] == ["A", "B"]
    assert result["values"] == [2, 1]


from datetime import datetime

from app.analytics import launch_frequency


def test_launch_frequency_by_month_and_year():
    result = launch_frequency(launches)

    assert result["labels"] == [2020, 2021]

    # 2020: January has 2 launches
    assert result["values"][0][0] == 2

    # 2021: March has 1 launch
    assert result["values"][1][2] == 1


def test_rocket_success_rate_empty_list():
    """Test with no launches."""
    result = rocket_success_rate([], rockets)
    assert result["labels"] == []
    assert result["values"] == []


def test_rocket_success_rate_none_success():
    """Test with None success values."""
    launches = [
        Launch(
            id="1",
            name="Test",
            date_utc="2020-01-01T00:00:00Z",
            date_unix=0,
            rocket="r1",
            launchpad="p1",
            success=None,
            details=None,
            links={},
        )
    ]
    result = rocket_success_rate(launches, rockets)
    assert len(result["values"]) == 1
    assert result["values"][0] == 0  # None treated as failure
