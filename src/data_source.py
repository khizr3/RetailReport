"""
This is a helper file that creates a DataSources object with loaded data stored as object variables

Author: Khizr Ali Khizr89@gmail.com

Created: June 9th, 2022
"""
# Imports
import pandas as pd  # Using DataFrames to store and manipulate data
import re
from selenium import webdriver  # Needed to get CAPS demographic data
from selenium.webdriver.chrome.options import Options  # Needed to set options for webdriver
from selenium.webdriver.chrome.service import Service  # Needed to install webdriver if not in cache
from selenium.webdriver.common.by import By  # Needed to select web attributes
from webdriver_manager.chrome import ChromeDriverManager  # Needed to install webdriver if not in cache


def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # s = Service(ChromeDriverManager(log_level=0).install())
    driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=chrome_options)
    return driver


def get_2010_census_caps():
    caps_2010 = pd.read_csv('../data/2010_caps_data.csv')
    caps_2010['TractNumber'] = caps_2010['Geographic Area Name'].str.split(',')
    caps_2010['TractNumber'] = caps_2010['TractNumber'].str.get(0).str[13:] + caps_2010['TractNumber'].str.get(1)
    caps_2010['TractNumber'] = caps_2010['TractNumber'].str[:-7]
    print('2010 Census CAPS Data Loaded')
    return caps_2010


def get_2020_census_caps():
    caps_2020 = pd.read_csv('../data/2020_caps_data.csv')
    caps_2020['TractNumber'] = caps_2020['Geographic Area Name'].str.split(',')
    caps_2020['TractNumber'] = caps_2020['TractNumber'].str.get(0).str[13:] + caps_2020['TractNumber'].str.get(1)
    caps_2020['TractNumber'] = caps_2020['TractNumber'].str[:-7]
    print('2020 Census CAPS Data Loaded')
    return caps_2020


# A class for retrieving ACS data from the MCDC Missouri Website
# Requires an address from which to retrieve coordinates
class ACSData:
    def __init__(self, location_coordinates):
        self.lat = location_coordinates[0]
        self.long = location_coordinates[1]
        self.current_driver = init_driver()
        url_2020 = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.capsACS.sas&_SERVICE=MCDC_long&' \
                   'latitude={}&longitude={}&radii=0.5%2C0.75%2C1%2C1.25&sitename=&dprofile=on&eprofile=on&' \
                   'sprofile=on&hprofile=on&units=+&printdetail=on'.format(self.lat, self.long)
        self.current_driver.get(url_2020)
        self.driver_2010 = init_driver()
        self.driver_2000 = init_driver()

    # Method that gets the 2000 CAPS information and aggregates it into one table
    def get_2000_pop_hh(self):
        """

        param coordinates: <List>
            A list of the latitude and longitude of the site location
        return: caps_2010 <pandas.DataFrame>
            a DataFrame with 2010 CAPS information loaded at the 4 required radius levels
        """
        pop_hh_2000 = [[0, 0]]
        for radius in [0.75, 1, 1.25]:
            url = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.caps2000.sas&_debug=&latitude={}&' \
                  'longitude={}&radii={}&sitename=&tablelist=all&units=+'.format(self.lat, self.long, radius)
            self.driver_2000.get(url)
            population = self.driver_2000.find_element(By.XPATH, '//*[@id="body"]/table/tbody[2]/tr[49]/td[2]')
            households = self.driver_2000.find_element(By.XPATH, '//*[@id="body"]/table/tbody[2]/tr[50]/td[2]')
            pop_hh_2000.append([int(population.get_attribute('innerHTML').replace(",", "")),
                                int(households.get_attribute('innerHTML').replace(",", ""))])
        pop_hh_2000[0][0] = (pop_hh_2000[1][0] + pop_hh_2000[2][0] + pop_hh_2000[3][0]) / 4
        pop_hh_2000[0][1] = (pop_hh_2000[1][1] + pop_hh_2000[2][1] + pop_hh_2000[3][1]) / 4
        print('2000 Population and Households Loaded')
        return pop_hh_2000

    def get_current_caps(self):
        """

        param driver: <selenium.webdriver>
            a chrome webdriver that is initialized at the CAPS ACS Page
        return: acs_table <pandas.DataFrame>
            a pandas dataframe containing all the ACS data at the required radii level
        """
        table_link = self.current_driver.find_element(By.XPATH, '//*[@id="body"]/p[1]/a').get_attribute('href')
        acs_table = pd.read_csv(table_link)
        acs_table['MedianHHInc'] = acs_table['MedianHHInc'].str.replace('[^0-9]', '', regex=True).astype('int')
        acs_table['TotHHs'] = acs_table['TotHHs'].str.replace('[^0-9]', '', regex=True).astype('int')
        print('Current CAPS ACS Table Loaded')
        return acs_table

    def get_current_af_table(self):
        """

        param driver: <selenium.webdriver>
            a chrome webdriver that is initialized at the CAPS ACS Page
        return: af_table <pandas.DataFrame>
            a pandas dataframe containing all the apportioned factor data at the required radii level
        """
        tables = self.current_driver.find_elements(By.CLASS_NAME, 'table')
        af_table = pd.DataFrame()
        for table in tables[5:]:
            html_string = table.get_attribute('outerHTML')
            af = pd.read_html(html_string)[0]  # apportioning factor
            af = af[af['Tract'].notnull()]
            af['County Cd'] = af['County Cd'].str[:-3]
            af = af.astype({'Tract': 'str'})
            af.loc[af['Tract'].str[-1] == '0', 'Tract'] = af['Tract'].str[:-2]
            af['Tract'] = af['Tract'] + ' ' + af['County Cd']
            af = af.groupby(af['Tract']).aggregate({'Tract': 'first', 'Radius': 'first', 'blkpop_': 'sum'})
            af_table = pd.concat([af_table, af], ignore_index=True)
        af_table = af_table.astype({'Radius': 'float'})
        af_table.rename(columns={'blkpop_': 'Total population'}, inplace=True)
        print('Current Apportioning Factor Table Loaded')
        return af_table

    def get_2010_af_table(self):
        """
        param coordinates: <List>
            A list of the latitude and longitude of the site location
        return: households <List>
            a List with 2010 Households loaded at the 4 required radius levels
        """
        af_table = pd.DataFrame()
        for radius in [0.5, 0.75, 1, 1.25]:
            url = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.caps2010.sas&_debug=&latitude={}&' \
                  'longitude={}&radii={}&sitename=&units=+&printdetail=on'.format(self.lat, self.long, radius)
            self.driver_2010.get(url)
            tables = self.driver_2010.find_elements(By.CLASS_NAME, 'table')
            temp_table = pd.read_html(tables[0].get_attribute('outerHTML'))[0]
            temp_table = temp_table[temp_table['GeoCode'].notnull()]
            temp_table['County Cd'] = temp_table['County Cd'].str[:-3]
            temp_table['Tract'] = temp_table['GeoCode'].str.split('-').str.get(1)
            temp_table.loc[temp_table['Tract'].str[-2:] == '00', 'Tract'] = temp_table['Tract'].str[:-3]
            temp_table['Tract'] = temp_table['Tract'] + ' ' + temp_table['County Cd']
            temp_table = temp_table.groupby(temp_table['Tract']).aggregate(
                {'Tract': 'first', 'Radius': 'first', 'Total population': 'sum'})
            af_table = pd.concat([af_table, temp_table], ignore_index=True)
        print('2010 Apportioning Factor Table Loaded')
        return af_table

    def quit_drivers(self):
        self.driver_2000.close()
        self.driver_2000.quit()
        print('Driver_2000 Closed')
        self.driver_2010.close()
        self.driver_2010.quit()
        print('Driver_2010 Closed')
        self.current_driver.close()
        self.current_driver.quit()
        print('Driver_Current Closed')
