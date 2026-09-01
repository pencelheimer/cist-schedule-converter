import csv
from datetime import datetime
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, vDDDTypes

def should_exclude(subject: str, exclude_list: list[str]) -> bool:
    return any([word == subject for word in exclude_list])

def convert_csv_to_ics(
    csv_content: str,
    group_id: int | str,
    exclude_list: list[str] | None = None,
) -> bytes:
    vcal = Calendar()
    vcal["prodid"] = "-//CIST Schedule Converter//cist.nure.ua//EN"
    vcal["version"] = "2.0"
    vcal["x-wr-calname"] = f"Schedule Group {group_id}"

    tz = ZoneInfo("Europe/Kyiv")
    reader = csv.DictReader(csv_content.splitlines())

    idx = 0
    for row in reader:
        event = Event()

        raw_topic = row.get("Тема", "")
        if not raw_topic:
            continue

        subject, event_type, *_ = raw_topic.split(" ")
        if should_exclude(subject, exclude_list or []):
            continue

        event["summary"] = f"{subject} | {event_type}"
        event["categories"] = [event_type]

        start_date_str = row.get("Дата начала")
        start_time_str = row.get("Время начала")
        end_date_str = row.get("Дата завершения")
        end_time_str = row.get("Время завершения")

        if not (start_date_str and start_time_str and end_date_str and end_time_str):
            continue

        event["dtstart"] = vDDDTypes(datetime.strptime(
                f"{start_date_str} {start_time_str}",
                "%d.%m.%Y %H:%M:%S"
            ).replace(tzinfo=tz))
        event["dtend"] = vDDDTypes(datetime.strptime(
                f"{end_date_str} {end_time_str}",
                "%d.%m.%Y %H:%M:%S"
            ).replace(tzinfo=tz))

        event["description"] = f"{start_time_str[:5]} - {end_time_str[:5]}"

        idx += 1
        event["uid"] = f"cist-{group_id}-{start_date_str}-{start_time_str}-{idx}@cist.nure.ua"

        vcal.add_component(event)

    return vcal.to_ical()
