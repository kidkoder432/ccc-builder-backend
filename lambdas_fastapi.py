from getArticulationsFromPrimaryCCC import *
from checkWhitelistedCourses import *
from parseTemplates import *

from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from typing import List

import uvicorn

app = FastAPI()

headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "connection": "keep-alive",
        "cookie": "ARRAffinity=0f60106f5ba8f78edacc2698bdde648fc9ccae752f545c6d9b8d13c2be8a63f2; ARRAffinitySameSite=0f60106f5ba8f78edacc2698bdde648fc9ccae752f545c6d9b8d13c2be8a63f2",
        "dnt": "1",
        "host": "assist.org",
        "prefer": "safe",
        "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    }
async def lambda_handler_primary(inputs):

    articulations = []

    async with aiohttp.ClientSession(headers=headers) as session:
        for item in inputs:

            cccId, fyId, yr, majorId = parseBody(item)

            x = await getArticulations(session, fyId, cccId, yr, majorId)

            articulations.append(x)
            yield x


async def lambda_handler_whitelist(inputs):

    articulatedCourses = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for item in inputs:

            cccId, fyId, yr, majorId = parseBody(item)

            cccCourses = inputs.get("cccCourses", [])
            artics = inputs.get("artics", {})

            x = await checkArticulations(session, fyId, cccId, yr, majorId, cccCourses, artics)

            articulatedCourses.append(x)
            yield x


async def lambda_handler_template(inputs):

    reqs = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for item in inputs:

            cccId, fyId, yr, majorId = parseBody(item)

            x = await parseArticulationRequirements(session, fyId, cccId, yr, majorId)
            yield json.dumps(x) + "\n"
            
def parseBody(body={}):
    cccId = body.get("cccId", 113)
    fyId = body.get("fyId", 79)
    yr = body.get("yr", 75)
    majorId = body.get(
        "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
    )

    return cccId, fyId, yr, majorId


class InputObject(BaseModel):
    cccId: int = 113
    fyId: int = 79
    yr: int = 75
    majorId: str = "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"

class InputWhitelistObject(BaseModel):
    cccId: int = 113
    fyId: int = 79
    yr: int = 75
    majorId: str = "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
    cccCourses: List[str] = []
    artics: dict = {}

@app.post("/primary")
async def route_primary(inputs: List[InputObject] = []):

    inputs = [dict(item) for item in inputs]

    return StreamingResponse(
        lambda_handler_primary(inputs),
        media_type="application/json",
    )


@app.post("/whitelist")
async def route_whitelist(inputs: List[InputWhitelistObject] = []):

    inputs = [dict(item) for item in inputs]

    return StreamingResponse(
        lambda_handler_whitelist(inputs),
        media_type="application/json",
    )


@app.post("/template")
async def route_template(inputs: List[InputObject] = []):

    inputs = [dict(item) for item in inputs]

    return StreamingResponse(
        lambda_handler_template(inputs),
        media_type="application/json",
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)