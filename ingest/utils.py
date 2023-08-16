from datetime import date, datetime

def get_key(x) :
    if x == "":
        return 0
    return x

Y = 2000 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
           ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
           ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
           ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
           ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]

def get_season_average_consumption(chart_data):
    avg = {
        "winter": {
            "count": 0,
            "value": 0
        },
        "spring":  {
            "count": 0,
            "value": 0
        },
        "summer":  {
            "count": 0,
            "value": 0
        },
        "autumn":  {
            "count": 0,
            "value": 0
        }
    }

    result = {
        "winter" : 0,
        "spring" : 0,
        "summer" : 0,
        "autumn" : 0
    }

    for item in chart_data:
        date = datetime.strptime(item["x"], "%Y-%m-%dT%H:%M:%S%z")
        if isinstance(date, datetime):
            date = date.date()
        date = date.replace(year=Y)
        res_season = next(season for season, (start, end) in seasons
                    if start <= date <= end)
        
        avg[res_season]["value"] += item["y"] if item["y"] != "" else 0
        avg[res_season]["count"] += 1

    result["winter"] = avg["winter"]["value"] / avg["winter"]["count"]
    result["spring"] = avg["spring"]["value"] / avg["spring"]["count"]
    result["summer"] = avg["summer"]["value"] / avg["summer"]["count"]
    result["autumn"] = avg["autumn"]["value"] / avg["autumn"]["count"]

    return result


