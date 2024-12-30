from csv import writer
import json

institutions = json.load(open('institutions.json'))

currentYear = 2024
currentYearId = 75

with open('fouryears.csv', 'w') as f:
    with open("ccc.csv", "w") as c:
        w = writer(f)
        wc = writer(c)
        for inst in institutions:
            if inst["isCommunityCollege"]:
                wc.writerow([inst['id'], inst['names'][0]['name'], inst['code'].strip()])
            else:
                w.writerow([inst['id'], inst['names'][0]['name'], inst['code'].strip()])

with open("terms.csv", "w") as f:
    w = writer(f)
    for year in range(currentYearId, -1, -1):
        w.writerow([f"{2024 - 75 + year}-{2024 - 74 + year}", year])