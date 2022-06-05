"""
This Program is intended to scrape data needed to conduct a Retail Site Analysis of any given area. Once scraped, the
file will aggregate and model data and come up with a projection report in the form of an Excel file. We hope to also
include a PDF report as an extended feature.
Currently, fitted for Texas with expansion features added as necessary

Author: Khizr Ali Khizr89@gmail.com

Created: May 23rd, 2022
"""
# Imports
import pandas as pd  # Using DataFrames to store and manipulate data
from geopy.geocoders import Nominatim
from selenium import webdriver  # Needed to get CAPS demographic data
from selenium.webdriver.chrome.options import Options  # Needed to set options for webdriver
from selenium.webdriver.chrome.service import Service  # Needed to install webdriver if not in cache
from selenium.webdriver.common.by import By  # Needed to select web attributes
from webdriver_manager.chrome import ChromeDriverManager  # Needed to install webdriver if not in cache


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
    print(location.raw)
    return [location.latitude, location.longitude]


# Method to start the driver and get it to the CAPS info page
def init_acs_driver(coordinates):
    """

    param coordinates: <List>
        A list of the latitude and longitude of the site location
    return: driver <selenium.webdriver>
        a selenium driver at the CAPS page with information loaded at the 4 required radius levels
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    url = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.capsACS.sas&_SERVICE=MCDC_long&' \
          'latitude={}&longitude={}&radii=0.5%2C0.75%2C1%2C1.25&sitename=&dprofile=on&eprofile=on&' \
          'sprofile=on&hprofile=on&units=+&printdetail=on'.format(coordinates[0], coordinates[1])
    driver.get(url)
    print('Driver Initialized')
    return driver


# Method that gets the 2000 CAPS information and aggregates it into one table
def get_2000_caps(coordinates):
    """

    param coordinates: <List>
        A list of the latitude and longitude of the site location
    return: caps_2010 <pandas.DataFrame>
        a DataFrame with 2010 CAPS information loaded at the 4 required radius levels
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    print('Driver Initialized')
    radii = [0.5, 0.75, 1, 1.25]
    caps_2000 = pd.DataFrame()
    for radius in radii:
        url = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.caps2000.sas&_debug=&latitude={}&' \
              'longitude={}&radii={}&sitename=&tablelist=all&units=+'.format(coordinates[0], coordinates[1], radius)
        driver.get(url)
        table_link = driver.find_element(By.XPATH, '//*[@id="body"]/p[1]/a').get_attribute('href')
        table = pd.read_csv(table_link)
        caps_2000 = pd.concat([caps_2000, table])
        print(radius, 'Mile Table Loaded')
    driver.close()
    print('2000 CAPS ACS Table Loaded')
    return caps_2000


# Method that gets the 2010 CAPS information and aggregates it into one table
def get_2010_households(coordinates):
    """

    param coordinates: <List>
        A list of the latitude and longitude of the site location
    return: households <List>
        a List with 2010 Households loaded at the 4 required radius levels
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    print('Driver Initialized')
    radii = [0.5, 0.75, 1, 1.25]
    households = []
    for radius in radii:
        url = 'https://mcdc.missouri.edu/cgi-bin/broker?_PROGRAM=apps.caps2010.sas&_debug=&' \
              'latitude={}&longitude={}&radii={}&sitename=&units=+'.format(coordinates[0], coordinates[1], radius)
        driver.get(url)
        hh = driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody[2]/tr[66]/td[2]').get_attribute('innerHTML')
        households.append(hh)
        print(radius, 'Mile Households Loaded')
    driver.close()
    print('2010 Households Loaded')
    return households


# Method to get CAPS profile of given coordinates
def get_caps(driver):
    """

    param driver: <selenium.webdriver>
        a chrome webdriver that is initialized at the CAPS ACS Page
    return: acs_table <pandas.DataFrame>
        a pandas dataframe containing all the ACS data at the required radii level
    """
    table_link = driver.find_element(By.XPATH, '//*[@id="body"]/p[1]/a').get_attribute('href')
    acs_table = pd.read_csv(table_link)
    print('CAPS ACS Table Loaded')
    return acs_table


# Method to get a table of the apportioning factor of the site
def get_af_table(driver):
    """

    param driver: <selenium.webdriver>
        a chrome webdriver that is initialized at the CAPS ACS Page
    return: af_table <pandas.DataFrame>
        a pandas dataframe containing all the apportioned factor data at the required radii level
    """
    tables = driver.find_elements(By.CLASS_NAME, 'table')
    af_table = pd.read_html(tables[5].get_attribute('outerHTML'))[0]
    for table in tables[6:]:
        html_string = table.get_attribute('outerHTML')
        af = pd.read_html(html_string)[0]  # apportioning factor
        af_table = pd.concat([af_table, af], ignore_index=True)
    af_table = af_table[af_table['Radius'] != 'Total forradius']
    print('Apportioning Factor Table Loaded')
    return af_table


# Method to create the trade area table
def create_trade_area(acs_table):
    trade_area = pd.DataFrame()
    # pd.Series(['2020 Population', '0.75-Mile', ])


# Method to fill in race and ethnicity values for the Demand Report
def get_race_ethnicity(acs_table):
    """

    :param acs_table: <pandas.DataFrame>
        A DataFrame of the caps profile
    :return: df <pandas.DataFrame>
        A DataFrame containing the Race & Ethnicity part of the Demand Report
    """
    df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                       '1.25-Mile Radius': []})
    df.loc[len(df.index)] = ['RACE & ETHNICITY', '', '', '', '']
    df.loc[len(df.index)] = ['% 2019 White Alone', acs_table['pctWhite1'][0], acs_table['pctWhite1'][1],
                             acs_table['pctWhite1'][2], acs_table['pctWhite1'][3]]
    df.loc[len(df.index)] = ['% 2019 Black or African American Alone', acs_table['pctBlack1'][0],
                             acs_table['pctBlack1'][1], acs_table['pctBlack1'][2], acs_table['pctBlack1'][3]]
    df.loc[len(df.index)] = ['% 2019 American Indian and Alaska Native Alone', acs_table['pctIndian1'][0],
                             acs_table['pctIndian1'][1], acs_table['pctIndian1'][2], acs_table['pctIndian1'][3]]
    df.loc[len(df.index)] = ['% 2019 Asian Alone', acs_table['pctAsian1'][0], acs_table['pctAsian1'][1],
                             acs_table['pctAsian1'][2], acs_table['pctAsian1'][3]]
    df.loc[len(df.index)] = ['% 2019 Native Hawaiian and OPI alone', acs_table['pctHawnPI1'][0],
                             acs_table['pctHawnPI1'][1], acs_table['pctHawnPI1'][2], acs_table['pctHawnPI1'][3]]
    df.loc[len(df.index)] = ['% 2019 Some Other Race alone', acs_table['pctOther1'][0], acs_table['pctOther1'][1],
                             acs_table['pctOther1'][2], acs_table['pctOther1'][3]]
    df.loc[len(df.index)] = ['% 2019 Two or More Races', acs_table['pctMultiRace'][0], acs_table['pctMultiRace'][1],
                             acs_table['pctMultiRace'][2], acs_table['pctMultiRace'][3]]
    df.loc[len(df.index)] = ['', '', '', '', '']
    df.loc[len(df.index)] = ['% 2019 Hispanic', acs_table['pctHispanicPop'][0], acs_table['pctHispanicPop'][1],
                             acs_table['pctHispanicPop'][2], acs_table['pctHispanicPop'][3]]
    df.loc[len(df.index)] = ['% 2019 Not Hispanic', acs_table['pctNonHispPop'][0], acs_table['pctNonHispPop'][1],
                             acs_table['pctNonHispPop'][2], acs_table['pctNonHispPop'][3]]
    df.loc[len(df.index)] = ['', '', '', '', '']
    print('Race and Ethnicity Values Completed')
    return df


def create_demand_report(acs_table, acs_table_2010):
    trade_area = pd.DataFrame()
    # population_density = get_population_density() # Need to load in 2010 data
    # household_trend = get_household_trend(get_2010_households(location_coordinates)) # Need to load in 2010 data
    # income = get_income()
    race_ethnicity = get_race_ethnicity(acs_table)
    # trade_area = pd.concat(trade_area, ['POPULATION TREND', '', '', ''])




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    location_address = input('Enter the Address for which you would like your report: \n')
    location_coordinates = get_lat_long(location_address)
    location_2000_acs = get_2000_caps(location_coordinates)

    location_acs_driver = init_acs_driver(location_coordinates)
    location_acs_table = get_caps(location_acs_driver)
    location_af_table = get_af_table(location_acs_driver)
    location_acs_driver.close()

    get_race_ethnicity(location_acs_table)
