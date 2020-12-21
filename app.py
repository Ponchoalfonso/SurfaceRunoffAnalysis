
from netCDF4 import Dataset, num2date
from xlsxwriter import Workbook
import numpy as np
from sys import exit
# Custom functions
from src.countries import CountryChecker, Point
from src.progressbar import printProgressBar
from src.spreadsheets import add_measurement, set_headers
from src.array_search import find, findLast, findIndex, findLastIndex, findMany


def get_stats(collection):
    m = np.mean(collection)
    mi = np.min(collection)
    ma = np.max(collection)

    return {"mean": m, "min": mi, "max": ma}


def mrro_stats_year(ws: Workbook.worksheet_class, measurements, year_values):
    current = 0
    total = len(measurements) * len(year_values)
    for measure in measurements:
        for yi, year in enumerate(measure["mrro"]):
            # Remove all 0 values
            values = np.array(year)
            mask = values != 0
            values = values[mask]

            # Get statistics
            stats = get_stats(values)
            add_measurement(
                ws,
                {
                    "country": measure["country"],
                    "year": year_values[yi],
                    "mean": stats["mean"],
                    "max": stats["max"],
                    "min": stats["min"]
                },
                current
            )

            # Progress control
            current += 1
            printProgressBar(current, total, "Analyzing data:",
                             "Complete", 2, 25)


def main():
    # Setup the datasets
    ds_mrro = Dataset("./datasets/IEA_CMCC_Runoffanomalyallmonths.nc")
    # Setup world dataset and country checker
    cc = CountryChecker(
        "./datasets/world_borders_old/TM_WORLD_BORDERS-0.3.shp")

    # Open excel file
    wb = Workbook('./out/data.xlsx')

    # Setup data variables
    times = ds_mrro.variables["time"]
    dates = num2date(times[192:], times.units, times.calendar)
    mrros = ds_mrro.variables["ro"][192:]

    desired_years = [2016, 2017, 2018, 2019, 2020]
    year_ranges = []

    for year in desired_years:
        start = findIndex(dates, lambda d: d.year == year)
        end = findLastIndex(dates, lambda d: d.year == year)

        year_ranges.append((start, end))

    measurements = []

    total = len(mrros[0]) * len(mrros[0][0])
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
            measure = find(measurements, lambda m: m["country"] == country)
            if measure == None:
                measure = {
                    "country": country,
                    "mrro": [[]] * len(year_ranges)
                }
                measurements.append(measure)

            for idx, bnds in enumerate(year_ranges):
                start, end = bnds
                measure["mrro"][idx].append(mrros[start:end, lti, lni])

            # Progress control
            current += 1
            printProgressBar(current, total, "Collecting data:",
                             "Complete", 2, 25)

    # Compute statistics
    ws = wb.add_worksheet("statistics")
    set_headers(ws, ["Country", "Year", "Mean", "Max", "Min"])
    mrro_stats_year(ws, measurements, desired_years)

    ds_mrro.close()
    wb.close()


if __name__ == '__main__':
    main()
