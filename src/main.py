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
from reports import Reports, DemandReport, TradeArea

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # location_address = input('Enter the Address for which you would like your report: \n')
    # location_coordinates = get_lat_long(location_address)
    # data_object = data_source.DataSources(location_coordinates)
    # required_data = data_source.ACSData('2222 black oak dr sugar land')
    required_reports = Reports('2222 black oak dr sugar land')
    demand_report = required_reports.get_demand_report()
    trade_area = required_reports.get_trade_area()
    demand_report.to_excel('../reports/2222 black oak dr sugar land demand report.xlsx')
    trade_area.to_excel('../reports/2222 black oak dr sugar land trade area.xlsx')
    sys.exit()
