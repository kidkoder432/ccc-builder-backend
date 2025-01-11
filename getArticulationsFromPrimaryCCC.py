from calendar import c
from csv import reader
import requests
import json

from pprint import pprint
from pyperclip import copy


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


def getMajorData(fyId, cccId, yr):
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

    r = requests.get(MAJORS_URL.format(rid=fyId, sid=cccId, yr=yr), headers=headers)

    if r.status_code == 200:
        majors = r.json()
    else:
        raise requests.HTTPError("Failed to get majors")

    return majors


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


def getArticulations(fyId, cccId, yr, majorId):

    returnObj = {}

    cccId, cccName, cccCode = getCCCInfo(cccId)
    fyId, fyName, fyCode = getFYInfo(fyId)

    termName, termId = getYearInfo(yr)
    majorData = getMajorData(fyId, cccId, yr)
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

    r = requests.get(MAJORS_URL.format(rid=fyId, sid=cccId, yr=yr), headers=headers)

    if r.status_code == 200:

        print(ARTICS_URL.format(key=majorId))
        r = requests.get(ARTICS_URL.format(key=majorId))

        if r.status_code == 200:
            arts = r.json()

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

                            if articulationOption["courseConjunction"] == "Or":
                                print("OR")
                                for course in articulationOption["items"]:
                                    if course["type"] == "Course":
                                        if course["attributes"]:
                                            for attr in course["attributes"]:
                                                note += f"{attr['content']}; "

                                        courseTitle = course["courseTitle"]
                                        coursePrefix = course["prefix"]
                                        courseNumber = course["courseNumber"]
                                        courseId = str(
                                            course["courseIdentifierParentId"]
                                        )

                                        option = {
                                            "courseTitle": courseTitle,
                                            "courseNumber": courseNumber,
                                            "coursePrefix": coursePrefix,
                                            "courseId": courseId,
                                        }

                                        if note:
                                            option["note"] = note

                                        returnObj["articulatedCourses"][-1][
                                            "articulationOptions"
                                        ].append([option])

                                        print(
                                            f"  {courseTitle} ({coursePrefix} {courseNumber})"
                                        )
                                        if note:
                                            print(f"\t{note}")
                            else:
                                for course in articulationOption["items"]:
                                    if course["type"] == "Course":
                                        if course["attributes"]:
                                            for attr in course["attributes"]:
                                                note += f"{attr["content"]}; "

                                        courseTitle = course["courseTitle"]
                                        coursePrefix = course["prefix"]
                                        courseNumber = course["courseNumber"]
                                        courseId = str(
                                            course["courseIdentifierParentId"]
                                        )

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


if __name__ == "__main__":
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

    majors = getMajorData(fyId, cccId, yr)

    majorName = input("Enter the name of the major: ")
    majorId = getMajor(majorName, majors)
    print("Major ID is:", majorId)

    json.dump(
        getArticulations(fyId, cccId, yr, majorId),
        open("output.json", "w"),
        indent=4,
    )
