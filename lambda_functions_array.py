from getArticulationsFromPrimaryCCC import *
from checkWhitelistedCourses import *
from parseTemplates import *


def lambda_handler_primary(event, context):

    articulations = []
    for item in json.loads(event["body"]):

        cccId, fyId, yr, majorId = parseBody(item)

        x = getArticulations(fyId, cccId, yr, majorId)

        articulations.append(x)

    return {"statusCode": 200, "body": json.dumps(articulations)}


def lambda_handler_whitelist(event, context):

    body = json.loads(event["body"])
    
    articulatedCourses = []
    for item in body:
    
        cccId, fyId, yr, majorId = parseBody(item)

        cccCourses = body.get("cccCourses", [])
        artics = body.get("artics", {})

        x = checkArticulations(
            fyId, cccId, yr, majorId, cccCourses, artics
        )

        articulatedCourses.append(x)

    return {"statusCode": 200, "body": json.dumps(articulatedCourses)}


def lambda_handler_template(event, context):

    reqs = []
    for item in json.loads(event["body"]):

        print(item)

        cccId, fyId, yr, majorId = parseBody(item)

        x = parseArticulationRequirements(fyId, cccId, yr, majorId)

        reqs.append(x)

    return {
        "statusCode": 200,
        "body": json.dumps(reqs),
    }


def parseEvent(event, body={}):
    try:
        params = event["queryStringParameters"]
        cccId = params.get("cccId", 113)
        fyId = params.get("fyId", 79)
        yr = params.get("yr", 75)
        majorId = params.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )
    except KeyError:
        body = json.loads(event["body"])
        cccId = body.get("cccId", 113)
        fyId = body.get("fyId", 79)
        yr = body.get("yr", 75)
        majorId = body.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )

    return cccId, fyId, yr, majorId


def parseBody(body={}):
    cccId = body.get("cccId", 113)
    fyId = body.get("fyId", 79)
    yr = body.get("yr", 75)
    majorId = body.get(
        "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
    )

    return cccId, fyId, yr, majorId
