from getArticulationsFromPrimaryCCC import *

def parseArticulationRequirements(fyId, cccId, yr, majorId):

    fyId = str(fyId)
    cccId = str(cccId)
    yr = str(yr)
    majorId = str(majorId)

    requiredCourses = []

    cccId, cccName, cccCode = getCCCInfo(cccId)
    fyId, fyName, fyCode = getFYInfo(fyId)

    termName, termId = getYearInfo(yr)
    majorData = getMajorData(fyId, cccId, yr)
    majorName = getMajorInfo(majorId, majorData)

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
            templateAssets = json.loads(r.json()["result"]["templateAssets"])
        for idx, item in enumerate(templateAssets):
            if item["type"] == "RequirementGroup":

                groupObj = {"requiredCourses": []}
                instructions = item["instruction"]

                if instructions:
                    if instructions["conjunction"] == "Or":
                        groupObj["conjunction"] = "Or"
                    else:
                        groupObj["conjunction"] = "And"

                for section in item["sections"]:

                    obj = {}
                    if section["type"] != "Section":
                        continue

                    if section["advisements"]:
                        for adv in section["advisements"]:
                            if adv["type"] == "NFollowing":
                                ncourses = int(adv["amount"])
                                print(
                                    f"Complete {ncourses} course{"s" if ncourses > 1 else ""} from the following:"
                                )
                                obj["type"] = "NCourses"
                                obj["amount"] = ncourses
                    else:
                        obj["type"] = "AllCourses"
                        print("Complete the following:")

                    reqs = []
                    for ridx, row in enumerate(section["rows"]):
                        print(f"--- Row {ridx + 1} ---")
                        for req in row["cells"]:
                            if req["type"] == "Course":
                                courseTitle = req["course"]["courseTitle"]
                                coursePrefix = req["course"]["prefix"]
                                courseNumber = req["course"]["courseNumber"]
                                if {
                                    "type": "Course",
                                    "courseTitle": courseTitle,
                                    "coursePrefix": coursePrefix,
                                    "courseNumber": courseNumber,
                                } not in reqs:
                                    reqs.append(
                                        {
                                            "type": "Course",
                                            "courseTitle": courseTitle,
                                            "coursePrefix": coursePrefix,
                                            "courseNumber": courseNumber,
                                        }
                                    )

                                print(
                                    f"{idx}: {courseTitle} ({coursePrefix} {courseNumber})"
                                )

                            elif req["type"] == "Series":
                                seriesTitle = req["series"]["name"]
                                print(f"{idx}: {seriesTitle}")
                                reqs.append(
                                    {
                                        "type": "Series",
                                        "seriesTitle": seriesTitle,
                                    }
                                )

                    obj["courses"] = reqs
                    groupObj["requiredCourses"].append(obj)
                requiredCourses.append(groupObj)
    return requiredCourses


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
        parseArticulationRequirements(fyId, cccId, yr, majorId),
        open("reqs.json", "w"),
        indent=4,
    )
