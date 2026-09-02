import csv
from datetime import datetime
from zoneinfo import ZoneInfo
from icalendar import Calendar, Event, vDDDTypes

from app.models import EventDescription, MeetingUrl

def should_exclude(event: EventDescription, exclude_list: list[EventDescription]) -> bool:
    return any(event == item for item in exclude_list)

def convert_csv_to_ics(
    csv_content: str,
    group_id: int | str,
    exclude_list: list[EventDescription] | None = None,
    attach_list: list[MeetingUrl] | None = None,
) -> bytes:
    vcal = Calendar()
    vcal["prodid"] = "-//CIST Schedule Converter//cist.nure.ua//EN"
    vcal["version"] = "2.0"
    vcal["x-wr-calname"] = f"Schedule Group {group_id}"

    tz = ZoneInfo("Europe/Kyiv")
    reader = csv.DictReader(csv_content.lstrip("\ufeff").splitlines())

    for idx, row in enumerate(reader):
        event = Event()

        raw_topic = row.get("Тема")
        if not raw_topic:
            continue

        event_description = EventDescription.from_cist_csv_topic(raw_topic)
        if should_exclude(event_description, exclude_list or []):
            continue

        event["summary"] = f"{event_description.subject} | {event_description.event_type}"
        event["categories"] = [event_description.event_type]

        attachment = next(
            (
                url for url in (attach_list or [])
                if url.subject == event_description.subject and url.event_type == event_description.event_type
            ),
            None
        )
        if attachment:
            event["url"] = attachment.url
            event["location"] = attachment.url

        start_date_str = row.get("Дата начала")
        start_time_str = row.get("Время начала")
        end_date_str = row.get("Дата завершения")
        end_time_str = row.get("Время завершения")

        if not (start_date_str and start_time_str and end_date_str and end_time_str):
            continue

        try:
            dt_start = datetime.strptime(f"{start_date_str} {start_time_str}", "%d.%m.%Y %H:%M:%S").replace(tzinfo=tz)
            dt_end = datetime.strptime(f"{end_date_str} {end_time_str}", "%d.%m.%Y %H:%M:%S").replace(tzinfo=tz)
        except ValueError:
            continue

        event["dtstart"] = vDDDTypes(dt_start)
        event["dtend"] = vDDDTypes(dt_end)
        event["description"] = f"{start_time_str[:5]} - {end_time_str[:5]}"
        event["uid"] = f"cist-{group_id}-{start_date_str}-{start_time_str}-{idx}@cist.nure.ua"

        vcal.add_component(event)

    return vcal.to_ical()
