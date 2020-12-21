from netCDF4 import Dataset, num2date


def main():
    # Setup the datasets
    ds_mrro = Dataset("./datasets/IEA_CMCC_Runoffanomalyallmonths.nc")
    times = ds_mrro.variables["time"]

    # for var in ds_mrro.variables.values():
    #     print(f"{var}\n")

    for ti, time in enumerate(num2date(times[192:], times.units, times.calendar)):
        print(f"Index: {ti}, {time}")

    # for lon in ds_mrro.variables["longitude"]:
    #     print(lon)


if __name__ == '__main__':
    main()
