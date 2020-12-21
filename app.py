
from netCDF4 import Dataset, num2date
from xlsxwriter import Workbook
import numpy as np
# Custom functions
from src.countries import CountryChecker, Point
from src.progressbar import printProgressBar
from src.spreadsheets import add_measurement, set_headers
from src.array_search import find, findIndex, findMany


def get_stats(collection):
    m = np.mean(collection)
    mi = np.min(collection)
    ma = np.max(collection)

    return {"mean": m, "min": mi, "max": ma}


def mrro_stats_year(ws: Workbook.worksheet_class, measurements):
    current = 0
    total = len(measurements) * 5
    for measure in measurements:
        for year in measure["mrro"].keys():
            values = list(map(lambda m: m["value"], measure["mrro"][year]))
            stats = get_stats(values)
            add_measurement(
                ws,
                {
                    "country": measure["country"],
                    "year": year,
                    "mean": stats["mean"],
                    "max": stats["max"],
                    "min": stats["min"]
                },
                current
            )
            current += 1
            printProgressBar(current, total, "Analyzing data:",
                             "Complete", 2, 25)


def main():
    # Setup the datasets
    ds_mrro = Dataset("./datasets/IEA_CMCC_Runoffanomalyallmonths.nc")

    # Open excel file
    wb = Workbook('./out/data.xlsx')
    ws = wb.add_worksheet("statistics")
    set_headers(ws, ["Country", "Year", "Mean", "Max", "Min"])

    times = ds_mrro.variables["time"]
    mrros = ds_mrro.variables["ro"][192:]

    # Setup world dataset and country checker
    cc = CountryChecker(
        "./datasets/world_borders_old/TM_WORLD_BORDERS-0.3.shp")

    measurements = []

    total = len(mrros) * len(mrros[0]) * len(mrros[0][0])
    current = 0
    # Iterate mrro dataset
    for lti, lat in enumerate(ds_mrro.variables["latitude"]):
        for lni, lon in enumerate(ds_mrro.variables["longitude"]):
            # Fixed longitude has a range between -180 and 180
            fLon = lon - 360 if lon > 180 else lon
            # Get country name
            c = cc.getCountry(Point(float(lat), float(fLon)))
            country = str(c)

            # Find existing country or create new one
            measure = {}
            mi = findIndex(measurements, lambda m: m["country"] == country)
            if mi != -1:
                measure = measurements[mi]
            else:
                # Save values in memory
                measure["country"] = country
                measure["mrro"] = {}
                measurements.append(measure)

            for ti, time in enumerate(num2date(times[192:], times.units, times.calendar)):
                current += 1

                # Total Runoff
                mrro = mrros[ti][lti][lni]

                if mrro > 0:
                    row = {
                        "time": str(time),
                        "lat": float(lat),
                        "lon": float(fLon),
                        "value": mrro
                    }

                    if not str(time.year) in measure["mrro"]:
                        measure["mrro"][str(time.year)] = []

                    # Save in memory
                    measure["mrro"][str(time.year)].append(row)

                    # print(
                    #     f"{time} Country: {country} lat: {lat}, lon: {fLon} {mrros.long_name}: {mrro}{mrros.original_units}")

                printProgressBar(current, total, "Collecting data:",
                                 "Complete", 2, 25)

    # Compute statistics
    ws = wb.get_worksheet_by_name("statistics")
    mrro_stats_year(ws, measurements)

    ds_mrro.close()
    wb.close()


if __name__ == '__main__':
    main()
