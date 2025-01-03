from csv import reader
import aiohttp
import asyncio
import json

MAJORS_URL = "https://assist.org/api/agreements?receivingInstitutionId={rid}&sendingInstitutionId={sid}&academicYearId={yr}&categoryCode=major"
ARTICS_URL = "https://assist.org/api/articulation/Agreements?Key={key}"

fouryears = list(reader(open("fouryears.csv")))
cc = list(reader(open("ccc.csv")))
terms = list(reader(open("terms.csv")))


def getCCCInfo(cccId):
    for row in cc:
        if row[0] == cccId:
            return row


def getFYInfo(fyId):
    for row in fouryears:
        if row[0] == fyId:
            return row


def getYearInfo(termId):
    for row in terms:
        if row[1] == termId:
            return row


def getMajorInfo(majorId, data):
    for major in data["reports"]:
        if major["key"] == majorId:
            return major["label"]


async def getMajorData(session, fyId, cccId, yr):

    async with session.get(MAJORS_URL.format(rid=fyId, sid=cccId, yr=yr)) as r:

        if r.status == 200:
            data = await r.json(content_type=None)
            return data
        else:
            raise aiohttp.ClientError("Failed to get majors")


def getTerm(year):
    for row in terms:
        if row[0].split("-")[0] == year:
            return row[1]

    return None


def getId(name="undefined", code="undefined"):
    for row in fouryears + cc:
        if name in row[1] or code in row[2]:
            return row[0]

    return None


def removeDuplicateArticulations(l):
    courses = []
    newList = []
    for articulation in l:
        if articulation["articulation"]["type"] == "Course":
            if (
                articulation["articulation"]["course"]["courseIdentifierParentId"]
                not in courses
            ):
                newList.append(articulation)
                courses.append(
                    articulation["articulation"]["course"]["courseIdentifierParentId"]
                )
        elif articulation["articulation"]["type"] == "Series":
            if articulation["articulation"]["series"]["name"] not in courses:
                newList.append(articulation)
                courses.append(articulation["articulation"]["series"]["name"])
    return newList


def getMajor(name="undefined", data={}):
    for major in data["reports"]:
        if name in major["label"]:
            return major["key"]


async def getArticulations(session, fyId, cccId, yr, majorId):

    returnObj = {}

    cccId, cccName, cccCode = getCCCInfo(cccId)
    fyId, fyName, fyCode = getFYInfo(fyId)

    termName, termId = getYearInfo(yr)
    majorData = await getMajorData(session, fyId, cccId, yr)
    majorName = getMajorInfo(majorId, majorData)

    returnObj["cccInfo"] = {"id": cccId, "name": cccName, "code": cccCode}
    returnObj["universityInfo"] = {"id": fyId, "name": fyName, "code": fyCode}

    returnObj["articulationInfo"] = {
        "term": termName,
        "termId": termId,
        "major": majorName,
        "majorId": majorId,
    }

    returnObj["articulatedCourses"] = []
    returnObj["nonArticulatedCourses"] = []

    async with session.get(
        ARTICS_URL.format(key=majorId),
    ) as r:

        if r.status == 200:
            arts = await r.json()

            requiredCourses = []
            print("Major: ", arts["result"]["name"])
            print("--- REQUIREMENTS ---")
            articulationData = json.loads(arts["result"]["articulations"])
            templates = json.loads(arts["result"]["templateAssets"])
            # copy(json.dumps(templates, indent=4))
            for idx, item in enumerate(templates):
                if item["type"] == "RequirementGroup":
                    for section in item["sections"]:
                        if section["type"] != "Section":
                            continue
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

                                    if reqobj not in requiredCourses:
                                        requiredCourses.append(reqobj)

                                    print(
                                        f"{idx}: {courseTitle} ({coursePrefix} {courseNumber}) [{courseId}]"
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

                                    requiredCourses.append(
                                        {
                                            "type": "Series",
                                            "seriesTitle": seriesTitle,
                                            "seriesId": seriesId,
                                        }
                                    )

            print("--- ARTICULATIONS WITH CURRENT COLLEGE ---")
            # print(articulationData)

            articulationData = removeDuplicateArticulations(articulationData)
            # copy(json.dumps(articulationData, indent=4))
            for articulation in articulationData:
                if articulation["articulation"]["type"] == "Course":

                    courseTitle = articulation["articulation"]["course"]["courseTitle"]
                    coursePrefix = articulation["articulation"]["course"]["prefix"]
                    courseNumber = articulation["articulation"]["course"][
                        "courseNumber"
                    ]
                    courseId = str(
                        articulation["articulation"]["course"][
                            "courseIdentifierParentId"
                        ]
                    )
                    courseCredits = articulation["articulation"]["course"]["maxUnits"]
                    print(f"{courseTitle} ({coursePrefix} {courseNumber})")

                    for course in requiredCourses[:]:
                        if (
                            course["type"] == "Course"
                            and course["courseId"] == str(courseId) + "_" + termId
                        ):
                            requiredCourses.remove(course)
                            break

                    articulatedCourses = articulation["articulation"][
                        "sendingArticulation"
                    ]["items"]

                    if articulation["articulation"]["sendingArticulation"][
                        "noArticulationReason"
                    ]:
                        requiredCourses.append(
                            {
                                "type": "NonArticulated",
                                "courseTitle": courseTitle,
                                "coursePrefix": coursePrefix,
                                "courseNumber": courseNumber,
                                "courseId": (str(courseId) + "_" + termId),
                                "reason": articulation["articulation"][
                                    "sendingArticulation"
                                ]["noArticulationReason"],
                            }
                        )
                        continue

                    returnObj["articulatedCourses"].append(
                        {
                            "articulationType": "Course",
                            "courseTitle": courseTitle,
                            "courseNumber": courseNumber,
                            "coursePrefix": coursePrefix,
                            "courseId": courseId,
                            "credits": courseCredits,
                            "articulationOptions": [],
                        }
                    )

                    for articulationOption in articulatedCourses:
                        print(
                            "--- Option {0} ---".format(
                                articulatedCourses.index(articulationOption) + 1
                            )
                        )

                        option = []
                        note = ""
                        if articulationOption["type"] == "CourseGroup":
                            for course in articulationOption["items"]:
                                if course["type"] == "Course":
                                    if course["attributes"]:
                                        for attr in course["attributes"]:
                                            note += f"{attr["content"]}; "

                                    courseTitle = course["courseTitle"]
                                    coursePrefix = course["prefix"]
                                    courseNumber = course["courseNumber"]
                                    courseId = str(course["courseIdentifierParentId"])

                                    option.append(
                                        {
                                            "courseTitle": courseTitle,
                                            "courseNumber": courseNumber,
                                            "coursePrefix": coursePrefix,
                                            "courseId": courseId,
                                        }
                                    )
                                    if note:
                                        option[-1]["note"] = note

                                    print(
                                        f"  {courseTitle} ({coursePrefix} {courseNumber})"
                                    )
                                    if note:
                                        print(f"\t{note}")
                        returnObj["articulatedCourses"][-1][
                            "articulationOptions"
                        ].append(option)

                elif articulation["articulation"]["type"] == "Series":

                    returnObj["articulatedCourses"].append(
                        {
                            "articulationType": "Series",
                            "seriesTitle": articulation["articulation"]["series"][
                                "name"
                            ],
                            "seriesId": "-".join(
                                [
                                    str(c["courseIdentifierParentId"])
                                    for c in articulation["articulation"]["series"][
                                        "courses"
                                    ]
                                ]
                            ),
                            "credits": sum(
                                [
                                    c["maxUnits"]
                                    for c in articulation["articulation"]["series"][
                                        "courses"
                                    ]
                                ]
                            ),
                            "courseSeries": [],
                            "articulationOptions": [],
                        }
                    )
                    for req in requiredCourses[:]:
                        if (
                            req["type"] == "Series"
                            and req["seriesId"]
                            == returnObj["articulatedCourses"][-1]["seriesId"]
                        ):
                            requiredCourses.remove(req)
                    for course in articulation["articulation"]["series"]["courses"]:
                        courseTitle = course["courseTitle"]
                        coursePrefix = course["prefix"]
                        courseNumber = course["courseNumber"]
                        courseId = str(course["courseIdentifierParentId"])
                        courseCredits = course["maxUnits"]
                        print(f"{courseTitle} ({coursePrefix} {courseNumber}) AND")

                        returnObj["articulatedCourses"][-1]["courseSeries"].append(
                            {
                                "courseTitle": courseTitle,
                                "courseNumber": courseNumber,
                                "coursePrefix": coursePrefix,
                                "courseId": courseId,
                                "credits": courseCredits,
                            }
                        )

                    articulatedCourses = articulation["articulation"][
                        "sendingArticulation"
                    ]["items"]
                    for articulationOption in articulatedCourses:
                        print(
                            "--- Option {0} ---".format(
                                articulatedCourses.index(articulationOption) + 1
                            )
                        )

                        option = []

                        if articulationOption["type"] == "CourseGroup":
                            for course in articulationOption["items"]:
                                if course["type"] == "Course":
                                    courseTitle = course["courseTitle"]
                                    coursePrefix = course["prefix"]
                                    courseNumber = course["courseNumber"]
                                    courseId = str(course["courseIdentifierParentId"])

                                    option.append(
                                        {
                                            "courseTitle": courseTitle,
                                            "courseNumber": courseNumber,
                                            "coursePrefix": coursePrefix,
                                            "courseId": courseId,
                                        }
                                    )
                                    print(
                                        f"  {courseTitle} ({coursePrefix} {courseNumber})"
                                    )
                        returnObj["articulatedCourses"][-1][
                            "articulationOptions"
                        ].append(option)

            if len(requiredCourses) > 0:
                print("--- NON-ARTICULATED COURSES ---")
                for i, requirement in enumerate(requiredCourses):
                    if requirement["type"] == "Series":
                        title = requirement["seriesTitle"]
                        print(f"#{i+1}: {title}")
                        returnObj["nonArticulatedCourses"].append(
                            {
                                "type": "Series",
                                "seriesTItle": title,
                                "seriesId": requirement["seriesId"],
                            }
                        )
                    elif requirement["type"] == "Course":
                        course = requirement["courseTitle"]
                        prefix = requirement["coursePrefix"]
                        number = requirement["courseNumber"]
                        courseId = str(requirement["courseId"])
                        print(f"#{i+1}: {course} ({prefix} {number}) [{courseId}]")
                        returnObj["nonArticulatedCourses"].append(
                            {
                                "type": "Course",
                                "courseTitle": course,
                                "coursePrefix": prefix,
                                "courseNumber": number,
                                "courseId": courseId,
                            }
                        )
                    elif requirement["type"] == "NonArticulated":
                        course = requirement["courseTitle"]
                        prefix = requirement["coursePrefix"]
                        number = requirement["courseNumber"]
                        courseId = str(requirement["courseId"])
                        reason = requirement["reason"]
                        print(f"#{i+1}: {course} ({prefix} {number})")
                        print(f'NOT ARTICULATED: "{reason}"')

                        returnObj["nonArticulatedCourses"].append(
                            {
                                "type": "Course",
                                "courseTitle": course,
                                "coursePrefix": prefix,
                                "courseNumber": number,
                                "courseId": courseId,
                                "reason": reason,
                            }
                        )

    return returnObj


async def main():
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

        majors = getMajorData(session, fyId, cccId, yr)

        majorName = input("Enter the name of the major: ")
        majorId = getMajor(majorName, majors)
        print("Major ID is:", majorId)

        data = await getArticulations(session, fyId, cccId, yr, majorId)

        json.dump(
            data,
            open("output.json", "w"),
            indent=4,
        )


if __name__ == "__main__":
    asyncio.run(main())
