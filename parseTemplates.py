from getArticulationsFromPrimaryCCC import *


async def parseArticulationRequirements(session, fyId, cccId, yr, majorId):

    fyId = str(fyId)
    cccId = str(cccId)
    yr = str(yr)
    majorId = str(majorId)

    requiredCourses = []

    cccId, cccName, cccCode = getCCCInfo(cccId)
    fyId, fyName, fyCode = getFYInfo(fyId)

    termName, termId = getYearInfo(yr)
    majorData = await getMajorData(session, fyId, cccId, yr)
    majorName = getMajorInfo(majorId, majorData)

    async with session.get(
        ARTICS_URL.format(key=majorId),
    ) as r:
        if r.status == 200:
            data = await r.json()
            templateAssets = json.loads(data["result"]["templateAssets"])
            for idx, item in enumerate(templateAssets):
                if item["type"] == "RequirementGroup":

                    groupObj = {"requiredCourses": []}
                    instructions = item["instruction"]

                    isSectionNFollowing = False
                    sectionNCourses = 0
                    sectionCredits = 0
                    needCreditInfo = False
                    if instructions:
                        if instructions.get("conjunction") == "Or":
                            groupObj["conjunction"] = "Or"
                        else:
                            groupObj["conjunction"] = "And"

                        if (
                            instructions["type"] == "NFromArea"
                            and instructions.get("amountUnitType", None) != "Course"
                        ):
                            needCreditInfo = True
                            sectionCredits = int(instructions["amount"])

                        elif instructions["type"] in ("NFromConjunction", "NFromArea"):
                            isSectionNFollowing = True
                            sectionNCourses = int(instructions["amount"])

                    for section in item["sections"]:

                        obj = {}
                        if section["type"] != "Section":
                            continue

                        if section["advisements"]:
                            for adv in section["advisements"]:
                                if (
                                    adv["type"] == "NFollowing"
                                    and adv.get("amountUnitType", None) != "Course"
                                ):
                                    needCreditInfo = True
                                    sectionCredits = int(adv["amount"])
                                    print(
                                        f"Complete {sectionCredits} credit{'s' if sectionCredits > 1 else ''} from the following:"
                                    )
                                    obj["type"] = "NCredits"
                                    obj["amount"] = sectionCredits

                                elif adv["type"] == "NFollowing":
                                    ncourses = int(adv["amount"])
                                    print(
                                        f"Complete {ncourses} course{"s" if ncourses > 1 else ""} from the following:"
                                    )
                                    obj["type"] = "NCourses"
                                    obj["amount"] = ncourses

                        elif isSectionNFollowing and sectionNCourses > 0:
                            obj["type"] = "NCourses"
                            obj["amount"] = sectionNCourses

                            print(
                                f"Complete {sectionNCourses} course{'s' if sectionNCourses > 1 else ''} from the following:"
                            )

                        elif needCreditInfo and sectionCredits > 0:
                            obj["type"] = "NCredits"
                            obj["amount"] = sectionCredits

                            print(
                                f"Complete {sectionCredits} credit{'s' if sectionCredits > 1 else ''} from the following:"
                            )

                        else:
                            obj["type"] = "AllCourses"
                            print("Complete all courses from the following:")

                        reqs = []
                        for ridx, row in enumerate(section["rows"]):
                            print(f"--- Row {ridx + 1} ---")
                            for req in row["cells"]:
                                if req["type"] == "Course":
                                    courseTitle = req["course"]["courseTitle"]
                                    coursePrefix = req["course"]["prefix"]
                                    courseNumber = req["course"]["courseNumber"]
                                    courseId = (
                                        str(req["course"]["courseIdentifierParentId"])
                                        + "_"
                                        + termId
                                    )

                                    reqobj = {
                                        "type": "Course",
                                        "courseTitle": courseTitle,
                                        "coursePrefix": coursePrefix,
                                        "courseNumber": courseNumber,
                                        "courseId": courseId,
                                        "credits": req["course"]["maxUnits"],
                                    }

                                    if reqobj not in reqs:
                                        reqs.append(reqobj)

                                    print(
                                        f"{idx}: {courseTitle} ({coursePrefix} {courseNumber})"
                                    )

                                elif req["type"] == "Series":
                                    seriesTitle = req["series"]["name"]
                                    print(f"{idx}: {seriesTitle}")

                                    seriesId = "-".join(
                                        [
                                            str(c["courseIdentifierParentId"])
                                            for c in req["series"]["courses"]
                                        ]
                                    )

                                    seriesId += "_" + termId

                                    reqs.append(
                                        {
                                            "type": "Series",
                                            "seriesTitle": seriesTitle,
                                            "seriesId": seriesId,
                                            "credits": str(
                                                sum(
                                                    [
                                                        c["maxUnits"]
                                                        for c in req["series"][
                                                            "courses"
                                                        ]
                                                    ]
                                                )
                                            ),
                                        }
                                    )

                        obj["courses"] = reqs
                        groupObj["requiredCourses"].append(obj)
                    requiredCourses.append(groupObj)
    return requiredCourses


async def main2():
    async with aiohttp.ClientSession() as session:
        print("Enter your primary CCC name or code: ", end="")
        name = input()
        if len(name) < 8:
            code = name.upper()
            print("CC ID is:", getId(code=code))
            cccId = getId(code=code)
        else:
            print("CC ID is:", getId(name=name))
            cccId = getId(name=name)

        print("Enter the name or code of the four year university: ", end="")
        name = input()
        if len(name) < 8:
            code = name.upper()
            print("FY ID is:", getId(code=code))
            fyId = getId(code=code)
        else:
            print("FY ID is:", getId(name=name))
            fyId = getId(name=name)

        print("Enter the academic year: ", end="")
        year = input()
        yr = getTerm(year)
        print("Term is :", yr)
        print(MAJORS_URL.format(rid=fyId, sid=cccId, yr=yr))

        majors = await getMajorData(session, fyId, cccId, yr)

        majorName = input("Enter the name of the major: ")
        majorId = getMajor(majorName, majors)
        print("Major ID is:", majorId)

        data = await parseArticulationRequirements(session, fyId, cccId, yr, majorId)
        json.dump(
            data,
            open("reqs.json", "w"),
            indent=4,
        )


if __name__ == "__main__":
    asyncio.run(main2())
