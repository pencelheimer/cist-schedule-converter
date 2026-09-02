from datetime import date
from typing import Annotated
from fastapi import FastAPI, Request, Query, Response
from pydantic import BeforeValidator
from starlette.middleware.base import RequestResponseEndpoint
import httpx

from .models import EventDescriptionFromQuery, Group, CistScheduleResponse, MeetingUrl, MeetingUrlFromQuery
from .converter import convert_csv_to_ics

app = FastAPI()

@app.middleware("http")
async def default_cache_control(request: Request, call_next: RequestResponseEndpoint):
    response = await call_next(request)
    response.headers["Cache-Control"] = f"public, max-age={ 60*60*12 }, stale-while-revalidate=600"
    return response

@app.get("/groups")
async def groups() -> set[Group]:
    async with httpx.AsyncClient() as client:
        response = (await client.get(
            "https://cist.nure.ua/ias/app/tt/P_API_GROUP_JSON"
        )).raise_for_status()
        content = response.content.decode('cp1251', errors="replace")

    uni = CistScheduleResponse.model_validate_json(content).university

    return uni.groups

@app.get("/groups/{group_id}/schedule")
async def get_group_schedule(
    group_id: int,
    from_date: Annotated[date, Query(alias="from")],
    to_date: Annotated[date, Query(alias="to")],
    exclude: Annotated[list[EventDescriptionFromQuery] | None, Query()] = None,
    attach: Annotated[ list[MeetingUrlFromQuery] | None, Query() ] = None
):
    params = {
        "ATypeDoc": "3",
        "Aid_potok": "0",
        "AMultiWorkSheet": "0",
        "Aid_group": str(group_id),
        "ADateStart": from_date.strftime("%d.%m.%Y"),
        "ADateEnd": to_date.strftime("%d.%m.%Y"),
    }

    async with httpx.AsyncClient() as client:
        resp = (await client.get(
            "https://cist.nure.ua/ias/app/tt/WEB_IAS_TT_GNR_RASP.GEN_GROUP_POTOK_RASP",
            params=params
        )).raise_for_status()
        content = resp.content.decode("cp1251", errors="replace")

    ics_data = convert_csv_to_ics(content, group_id=group_id, exclude_list=exclude, attach_list = attach)

    return Response(
        content=ics_data,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="schedule_{group_id}.ics"'},
    )
