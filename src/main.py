"""
This Program is intended to scrape data needed to conduct a Retail Site Analysis of any given area. Once scraped, the
file will aggregate and model data and come up with a projection report in the form of an Excel file. We hope to also
include a PDF report as an extended feature.
Currently, fitted for Texas with expansion features added as necessary

Author: Khizr Ali Khizr89@gmail.com

Created: May 23rd, 2022
"""
# Imports
import sys
import data_source
from competition import Competition
from reports import Reports, DemandReport, TradeArea
from geopy.geocoders import Nominatim


# Method to get the Latitude and Longitude of an address
def get_lat_long(address):
    """

    param address: <String>
        String of the address for which we want to get the latitude and longitude
    return: [lat,long] <List>
        List of the latitude and longitude of address provided
    """
    locator = Nominatim(user_agent="rsa-application")
    location = locator.geocode(address)
    print('Latitude = {}, Longitude = {}'.format(location.latitude, location.longitude))
    return [location.latitude, location.longitude]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # location_address = input('Enter the Address for which you would like your report: \n')
    location_coordinates = get_lat_long('2222 black oak dr sugar land')

    required_reports = Reports(location_coordinates)
    """
    demand_report = required_reports.get_demand_report()
    trade_area = required_reports.get_trade_area()
    demand_report.to_excel('../reports/2222 black oak dr sugar land demand report.xlsx')
    trade_area.to_excel('../reports/2222 black oak dr sugar land trade area.xlsx')
    """
    competition = Competition(location_coordinates).get_competition()
    sys.exit()
