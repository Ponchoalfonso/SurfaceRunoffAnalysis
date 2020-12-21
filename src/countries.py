
from osgeo import ogr


class Point(object):
    """ Wrapper for ogr point """

    def __init__(self, lat, lng):
        """ Coordinates are in degrees """
        self.point = ogr.Geometry(ogr.wkbPoint)
        self.point.AddPoint(lng, lat)

    def getOgr(self):
        return self.point
    ogr = property(getOgr)


class Country(object):
    """ Wrapper for ogr country shape. Not meant to be instantiated directly. """

    def __init__(self, shape):
        self.shape = shape

    def getIso(self):
        return self.shape.GetField('ISO2')
    iso = property(getIso)

    def __str__(self):
        return self.shape.GetField('NAME')

    def contains(self, point):
        return self.shape.geometry().Contains(point.ogr)


class CountryChecker(object):
    """ Loads a country shape file, checks coordinates for country location. """

    def __init__(self, country_file):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        self.countryFile = driver.Open(country_file)
        self.layer = self.countryFile.GetLayer()

    def getCountry(self, point):
        """
        Checks given gps-incoming coordinates for country.
        Output is either country shape index or None
        """

        nearest = {"country": None, "distance": 0}
        for i in range(self.layer.GetFeatureCount()):
            country = self.layer.GetFeature(i)

            if country.geometry().Contains(point.ogr):
                return Country(country)

            # If the point is not in the contry check if it is near to it
            distance = country.geometry().Distance(point.ogr)
            if nearest["country"] != None:
                if nearest["distance"] > distance:
                    nearest["country"] = country
                    nearest["distance"] = distance
            else:
                nearest["country"] = country
                nearest["distance"] = distance

        # Return the nearest country if the point is not contained by any
        return Country(nearest["country"])
