from getArticulationsFromPrimaryCCC import *
from checkWhitelistedCourses import *
from parseTemplates import *


def lambda_handler_primary(event, context):

    params = event["queryStringParameters"]

    body = json.loads(event["body"])

    try:
        params = event["queryStringParameters"]
        cccId = params.get("cccId", 113)
        fyId = params.get("fyId", 79)
        yr = params.get("yr", 75)
        majorId = params.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )
    except KeyError:
        cccId = body.get("cccId", 113)
        fyId = body.get("fyId", 79)
        yr = body.get("yr", 75)
        majorId = body.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )

    articulations = getArticulations(fyId, cccId, yr, majorId)

    return {"statusCode": 200, "body": json.dumps(articulations)}


def lambda_handler_whitelist(event, context):

    print(event)
    body = json.loads(event["body"])

    try:
        params = event["queryStringParameters"]
        cccId = params.get("cccId", 113)
        fyId = params.get("fyId", 79)
        yr = params.get("yr", 75)
        majorId = params.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )
    except KeyError:
        cccId = body.get("cccId", 113)
        fyId = body.get("fyId", 79)
        yr = body.get("yr", 75)
        majorId = body.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )

    cccCourses = body.get("cccCourses", [])
    artics = body.get("artics", {})

    articulatedCourses = checkArticulations(
        fyId, cccId, yr, majorId, cccCourses, artics
    )

    return {"statusCode": 200, "body": json.dumps(articulatedCourses)}


def lambda_handler_template(event, context):

    body = json.loads(event["body"])

    try:
        params = event["queryStringParameters"]
        cccId = params.get("cccId", 113)
        fyId = params.get("fyId", 79)
        yr = params.get("yr", 75)
        majorId = params.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )
    except KeyError:
        cccId = body.get("cccId", 113)
        fyId = body.get("fyId", 79)
        yr = body.get("yr", 75)
        majorId = body.get(
            "majorId", "75/113/to/79/Major/fc50cced-05c2-43c7-7dd5-08dcb87d5deb"
        )

    return {
        "statusCode": 200,
        "body": json.dumps(parseArticulationRequirements(fyId, cccId, yr, majorId)),
    }
