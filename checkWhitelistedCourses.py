from getArticulationsFromPrimaryCCC import getArticulations

async def checkArticulations(session, fyId, cccId, yr, majorId, cccCourses, artics={}):
    
    if not artics: 
        artics = await getArticulations(session, fyId, cccId, yr, majorId)

    articulatedCourses = []

    for articulation in artics["articulatedCourses"]:
        if articulation["articulationType"] == "Course":
            print(articulation["courseTitle"], end=": ")
            isArticulated = False
            for option in articulation["articulationOptions"]:
                articulationBooleans = []
                
                for course in option:
                    courseObj = {
                        "courseTitle": course["courseTitle"],
                        "courseNumber": course["courseNumber"],
                        "coursePrefix": course["coursePrefix"],
                    }
                    if courseObj not in cccCourses:
                        articulationBooleans.append(False)
                        break
                    else:
                        articulationBooleans.append(True)

                if all(articulationBooleans):
                    print("ARTICULATED")
                    isArticulated = True
                    break
            if isArticulated == False:
                print("NOT ARTICULATED")
            else:
                articulatedCourses.append(articulation)  
        elif articulation["articulationType"] == "Series":
            print(articulation["seriesTitle"], end=": ")
            isArticulated = False
            for option in articulation["articulationOptions"]:
                articulationBooleans = []
                
                for course in option:
                    courseObj = {
                        "courseTitle": course["courseTitle"],
                        "courseNumber": course["courseNumber"],
                        "coursePrefix": course["coursePrefix"],
                    }
                    if courseObj not in cccCourses:
                        articulationBooleans.append(False)
                        break
                    else:
                        articulationBooleans.append(True)

                if all(articulationBooleans):
                    print("ARTICULATED")
                    isArticulated = True
                    break
            if isArticulated == False:
                print("NOT ARTICULATED")
            else:
                articulatedCourses.append(articulation)

    return articulatedCourses