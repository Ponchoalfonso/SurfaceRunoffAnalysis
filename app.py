
from netCDF4 import Dataset, num2date
from xlsxwriter import Workbook
import numpy as np
from sys import exit
from time import time
import concurrent.futures
# Custom functions
from src.countries import CountryChecker, Point
from src.progressbar import printProgressBar
from src.spreadsheets import add_measurement, set_headers
from src.array_search import find, findLast, findIndex, findLastIndex, findMany


def stats_per_country(bounds, year_ranges):
    lower, upper = bounds

    # Setup the datasets
    ds_mrro = Dataset("./datasets/IEA_CMCC_Runoffanomalyallmonths.nc")
    # Setup world dataset and country checker
    cc = CountryChecker(
        "./datasets/world_borders_old/TM_WORLD_BORDERS-0.3.shp")

    mrros = ds_mrro.variables["ro"][192:, lower:upper]
    latitudes = ds_mrro.variables["latitude"][lower:upper]
    longitudes = ds_mrro.variables["longitude"]

    measurements = []

    # Iterate mrro dataset
    for lti, lat in enumerate(latitudes):
        for lni, lon in enumerate(longitudes):
            # Fixed longitude has a range between -180 and 180
            fLon = lon - 360 if lon > 180 else lon
            # Get country name
            c = cc.getCountry(Point(float(lat), float(fLon)))
            country = str(c)

            # Find existing country or create new one
            measure = find(measurements, lambda m: m["country"] == country)
            if measure == None:
                measure = {
                    "country": country,
                    "mrro": [{"sum": 0, "count": 0, "max": None, "min": None}] * len(year_ranges)
                }
                measurements.append(measure)

            for idx, bnds in enumerate(year_ranges):
                start, end = bnds
                ros = mrros[start:end, lti, lni]

                measure["mrro"][idx]["sum"] += np.sum(ros)
                measure["mrro"][idx]["count"] += len(ros)
                minimum = np.min(ros)
                maximum = np.max(ros)
                if measure["mrro"][idx]["max"] == None or measure["mrro"][idx]["max"] < maximum:
                    measure["mrro"][idx]["max"] = maximum
                if measure["mrro"][idx]["min"] == None or measure["mrro"][idx]["min"] > minimum:
                    measure["mrro"][idx]["min"] = minimum

    ds_mrro.close()
    return measurements


def merge_results(results):
    measures = []
    for measurements in results:
        for country in measurements:
            runoff = country["mrro"]
            measure = find(
                measures, lambda m: m["country"] == country["country"])

            if measure == None:
                measure = {
                    "country": country["country"],
                    "mrro": runoff
                }
                measures.append(measure)
            else:
                for yi, year in enumerate(measure["mrro"]):
                    year["sum"] += runoff[yi]["sum"]
                    year["count"] += runoff[yi]["count"]
                    if year["max"] < runoff[yi]["max"]:
                        year["max"] = runoff[yi]["max"]
                    if year["min"] < runoff[yi]["min"]:
                        year["min"] = runoff[yi]["min"]

    return measures


def main():
    # Setup the datasets
    ds_mrro = Dataset("./datasets/IEA_CMCC_Runoffanomalyallmonths.nc")

    # Open excel file
    wb = Workbook('./out/data.xlsx')

    # Setup data variables
    times = ds_mrro.variables["time"]
    dates = num2date(times[192:], times.units, times.calendar)
    latitudes = ds_mrro.variables["latitude"]

    desired_years = [2016, 2017, 2018, 2019, 2020]
    year_ranges = []

    for year in desired_years:
        start = findIndex(dates, lambda d: d.year == year)
        end = findLastIndex(dates, lambda d: d.year == year)

        year_ranges.append((start, end))

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Scatter data among processes
        processes = 4
        rest = len(latitudes) % processes
        step = int(len(latitudes) / processes)

        futures = []
        for rank in range(processes):
            start = (step * rank) - 1
            end = (step * (rank + 1)) - 1

            if (rank == 0):
                start = 0
            elif (rank == processes - 1):
                end += rest

            bounds = (start, end)

            futures.append(executor.submit(
                stats_per_country, bounds, year_ranges))

        results = []
        for f in concurrent.futures.as_completed(futures):
            result = f.result()
            results.append(result)

        measures = merge_results(results)

        # Summarize results
        ws = wb.add_worksheet("statistics")
        set_headers(ws, ["Country", "Year", "Mean", "Max", "Min"])

        row = 0
        for measure in measures:
            country = measure["country"]
            for yi, year in enumerate(desired_years):
                runoff = measure["mrro"][yi]
                # Get data
                mean = runoff["sum"] / runoff["count"]
                data = (country, year, mean, runoff["max"], runoff["min"])
                # Write data
                add_measurement(ws, data, row)
                row += 1

    ds_mrro.close()
    wb.close()


if __name__ == '__main__':
    print("Analysis started")
    start_time = time()
    main()
    execution_time = (time() - start_time) / 60 / 60
    print(f"Done in {execution_time}hrs")
