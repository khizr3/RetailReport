"""
This Program is intended to scrape data needed to conduct a Retail Site Analysis of any given area. Once scraped, the
file will aggregate and model data and come up with a projection report in the form of an Excel file. We hope to also
include a PDF report as an extended feature.
Currently, fitted for Texas with expansion features added as necessary

Author: Khizr Ali Khizr89@gmail.com

Created: May 23rd, 2022
"""
# Imports
import re
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
    print()
    return [location.latitude, location.longitude]


class CAPSData:
    """
    Necessary Categories:
    Population Trend and Density: 2010 Data, CURRENT CAPS, future projections
    Households Trend: 2000 Households 2010 Data, CURRENT CAPS, future projections
    Income: 2010 Data, CURRENT CAPS, future projections
    Household Vehicles: CURRENT CAPS
    Race & Ethnicity: CURRENT CAPS
    Education and Occupation: CURRENT CAPS
    Age and Occupancy: CURRENT CAPS
    Retail Sales Potential: CURRENT CAPS
    Household Expenditure: CURRENT CAPS
    """

    # Initialization method to get the required coordinates data
    def __init__(self, coordinates):
        self.lat = coordinates[0]
        self.long = coordinates[1]
        self.current_acs_driver = self.init_current_acs_driver()

    # Method to start the driver and get it to the CAPS info page
    def init_current_acs_driver(self):
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
              'sprofile=on&hprofile=on&units=+&printdetail=on'.format(self.lat, self.long)
        driver.get(url)
        print('Driver Initialized')
        return driver

    # Method to close the current_acs_driver
    def close(self):
        self.current_acs_driver.close()

    # Method to get CAPS profile of given coordinates
    def get_caps(self):
        """

        param driver: <selenium.webdriver>
            a chrome webdriver that is initialized at the CAPS ACS Page
        return: acs_table <pandas.DataFrame>
            a pandas dataframe containing all the ACS data at the required radii level
        """
        table_link = self.current_acs_driver.find_element(By.XPATH, '//*[@id="body"]/p[1]/a').get_attribute('href')
        acs_table = pd.read_csv(table_link)
        print('CAPS ACS Table Loaded')
        return acs_table

    # Method to get a table of the apportioning factor of the site
    def get_af_table(self):
        """

        param driver: <selenium.webdriver>
            a chrome webdriver that is initialized at the CAPS ACS Page
        return: af_table <pandas.DataFrame>
            a pandas dataframe containing all the apportioned factor data at the required radii level
        """
        tables = self.current_acs_driver.find_elements(By.CLASS_NAME, 'table')
        af_table = pd.read_html(tables[5].get_attribute('outerHTML'))[0]
        for table in tables[6:]:
            html_string = table.get_attribute('outerHTML')
            af = pd.read_html(html_string)[0]  # apportioning factor
            af_table = pd.concat([af_table, af], ignore_index=True)
        af_table = af_table[af_table['Radius'] != 'Total forradius']
        print('Apportioning Factor Table Loaded')
        return af_table


class Reports:
    # Initialization method to get the required coordinates data
    def __init__(self, current_acs_table):
        self.current_acs = current_acs_table
        self.median_income = self.current_acs['MedianHHInc'].tolist()
        for index, income in enumerate(self.median_income):
            self.median_income[index] = int(re.sub("[^0-9]", "", self.median_income[index]))
        self.__get_automotive_expenditure()

    # Method to create the trade area table
    def create_trade_area(self):
        trade_area = pd.DataFrame()
        # pd.Series(['2020 Population', '0.75-Mile', ])

    def create_demand_report(self):
        """
        Necessary Categories:
        Population Trend and Density: 2010 Data, CURRENT CAPS, future projections
        Households Trend: 2000 Households 2010 Data, CURRENT CAPS, future projections
        Income: 2010 Data, CURRENT CAPS, future projections
        Household Vehicles: CURRENT CAPS
        Race & Ethnicity: COMPLETE
        Education and Occupation: 2010 Data, CURRENT CAPS
        Age and Occupancy: CURRENT CAPS
        Retail Sales Potential: CURRENT CAPS
        Household Expenditure: CURRENT CAPS
        :return:
        """
        trade_area = pd.DataFrame()
        # population_density = get_population_density() # Need to load in 2010 data
        # household_trend = get_household_trend(get_2010_households(location_coordinates)) # Need to load in 2010 data
        # income = get_income()
        race_ethnicity = self.__get_race_ethnicity()
        education_occupation = self.__get_education_occupation()
        age_occupancy = self.__get_age_occupancy()
        automotive_expenditure = self.__get_automotive_expenditure()
        # trade_area = pd.concat(trade_area, ['POPULATION TREND', '', '', ''])

    # Method to fill in race and ethnicity values for the Demand Report
    def __get_race_ethnicity(self):
        """
        :return: df <pandas.DataFrame>
            A DataFrame containing the Race & Ethnicity part of the Demand Report
        """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['RACE & ETHNICITY', '', '', '', '']
        df.loc[1] = ['% 2019 White Alone', self.current_acs['pctWhite1'][0], self.current_acs['pctWhite1'][1],
                     self.current_acs['pctWhite1'][2], self.current_acs['pctWhite1'][3]]
        df.loc[2] = ['% 2019 Black or African American Alone', self.current_acs['pctBlack1'][0],
                     self.current_acs['pctBlack1'][1], self.current_acs['pctBlack1'][2],
                     self.current_acs['pctBlack1'][3]]
        df.loc[3] = ['% 2019 American Indian and Alaska Native Alone', self.current_acs['pctIndian1'][0],
                     self.current_acs['pctIndian1'][1], self.current_acs['pctIndian1'][2],
                     self.current_acs['pctIndian1'][3]]
        df.loc[4] = ['% 2019 Asian Alone', self.current_acs['pctAsian1'][0], self.current_acs['pctAsian1'][1],
                     self.current_acs['pctAsian1'][2], self.current_acs['pctAsian1'][3]]
        df.loc[5] = ['% 2019 Native Hawaiian and OPI alone', self.current_acs['pctHawnPI1'][0],
                     self.current_acs['pctHawnPI1'][1], self.current_acs['pctHawnPI1'][2],
                     self.current_acs['pctHawnPI1'][3]]
        df.loc[6] = ['% 2019 Some Other Race alone', self.current_acs['pctOther1'][0], self.current_acs['pctOther1'][1],
                     self.current_acs['pctOther1'][2], self.current_acs['pctOther1'][3]]
        df.loc[7] = ['% 2019 Two or More Races', self.current_acs['pctMultiRace'][0],
                     self.current_acs['pctMultiRace'][1], self.current_acs['pctMultiRace'][2],
                     self.current_acs['pctMultiRace'][3]]
        df.loc[8] = ['', '', '', '', '']
        df.loc[9] = ['% 2019 Hispanic', self.current_acs['pctHispanicPop'][0], self.current_acs['pctHispanicPop'][1],
                     self.current_acs['pctHispanicPop'][2], self.current_acs['pctHispanicPop'][3]]
        df.loc[10] = ['% 2019 Not Hispanic', self.current_acs['pctNonHispPop'][0], self.current_acs['pctNonHispPop'][1],
                      self.current_acs['pctNonHispPop'][2], self.current_acs['pctNonHispPop'][3]]
        df.loc[11] = ['', '', '', '', '']
        print('Race and Ethnicity Values Completed')
        return df

    def __get_education_occupation(self):
        """
                :return: df <pandas.DataFrame>
                    A DataFrame containing the Race & Ethnicity part of the Demand Report
                """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[len(df.index)] = ['EDUCATION & OCCUPATION', '', '', '', '']
        df.loc[len(df.index)] = ['EDUCATION', '', '', '', '']

        df.loc[len(df.index)] = ['', '', '', '', '']
        df.loc[len(df.index)] = ['OCCUPATION', '', '', '', '']

        return df

    def __get_age_occupancy(self):
        """
                :return: df <pandas.DataFrame>
                    A DataFrame containing the Race & Ethnicity part of the Demand Report
                """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[len(df.index)] = ['AGE & OCCUPANCY', '', '', '', '']
        df.loc[len(df.index)] = ['AGE', '', '', '', '']
        df.loc[len(df.index)] = ['% 2019 Total Population: Median Age', self.current_acs['MedianAge'][0],
                                 self.current_acs['MedianAge'][1], self.current_acs['MedianAge'][2],
                                 self.current_acs['MedianAge'][3]]
        df.loc[len(df.index)] = ['', '', '', '', '']
        df.loc[len(df.index)] = ['OCCUPANCY', '', '', '', '']
        df.loc[len(df.index)] = ['% 2019 Households', self.current_acs['TotHHs'][0], self.current_acs['TotHHs'][1],
                                 self.current_acs['TotHHs'][2], self.current_acs['TotHHs'][3]]
        df.loc[len(df.index)] = ['% 2019 Owner Occupied Housing Units', self.current_acs['MedianAge'][0],
                                 self.current_acs['MedianAge'][1], self.current_acs['MedianAge'][2],
                                 self.current_acs['MedianAge'][3]]
        df.loc[len(df.index)] = ['% 2019 Renter Occupied Housing Units', self.current_acs['MedianAge'][0],
                                 self.current_acs['MedianAge'][1], self.current_acs['MedianAge'][2],
                                 self.current_acs['MedianAge'][3]]
        return df

    def __get_automotive_expenditure(self):
        """
        :return: df <pandas.DataFrame>
            A DataFrame containing the Automotive Expenditures part of the Demand Report
        """

        AUTO_INTERCEPT = 681.1502774782
        AUTO_VAR_1 = 0.0314898282
        AUTO_VAR_2 = 0.000000128
        MAINTENANCE_INTERCEPT = 354.712725117
        MAINTENANCE_VAR_1 = 0.008887331
        MAINTENANCE_VAR_2 = 0.0000000145
        PCT_GASOLINE = 0.9130183561592
        PCT_DIESEL = 0.0218277844632
        PCT_GASOLINE_OOT = 0.0581867323745
        PCT_MOTOR_OIL = 0.0066710599202
        PCT_LUBE_OIL = 0.1143031164349
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['AUTOMOTIVE',
                     AUTO_INTERCEPT + (self.median_income[0] * AUTO_VAR_1) - (self.median_income[0] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (self.median_income[1] * AUTO_VAR_1) - (self.median_income[1] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (self.median_income[2] * AUTO_VAR_1) - (self.median_income[2] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (self.median_income[3] * AUTO_VAR_1) - (self.median_income[3] ** 2. * AUTO_VAR_2)]
        df.loc[1] = ['2019 Gasoline (Household Average)', df.iat[0, 1] * PCT_GASOLINE, df.iat[0, 2] * PCT_GASOLINE,
                     df.iat[0, 3] * PCT_GASOLINE, df.iat[0, 4] * PCT_GASOLINE]
        df.loc[2] = ['2019 Diesel Fuel (Household Average)', df.iat[0, 1] * PCT_DIESEL, df.iat[0, 2] * PCT_DIESEL,
                     df.iat[0, 3] * PCT_DIESEL, df.iat[0, 4] * PCT_DIESEL]
        df.loc[3] = ['2019 Gasoline on out-of-town trips (Household Average)', df.iat[0, 1] * PCT_GASOLINE_OOT,
                     df.iat[0, 2] * PCT_GASOLINE_OOT, df.iat[0, 3] * PCT_GASOLINE_OOT, df.iat[0, 4] * PCT_GASOLINE_OOT]
        df.loc[4] = ['2019 Motor Oil (Household Average)', df.iat[0, 1] * PCT_MOTOR_OIL, df.iat[0, 2] * PCT_MOTOR_OIL,
                     df.iat[0, 3] * PCT_MOTOR_OIL, df.iat[0, 4] * PCT_MOTOR_OIL]
        maintenance = [(self.median_income[0] * MAINTENANCE_VAR_1) - (self.median_income[0] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[1] * MAINTENANCE_VAR_1) - (self.median_income[1] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[2] * MAINTENANCE_VAR_1) - (self.median_income[2] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[3] * MAINTENANCE_VAR_1) - (self.median_income[3] ** 2 * MAINTENANCE_VAR_2)]
        for index, val in enumerate(maintenance):
            maintenance[index] = MAINTENANCE_INTERCEPT + val
        df.loc[5] = ['2019 Lube, oil change, and oil filters (Household Average)', maintenance[0] * PCT_LUBE_OIL,
                     maintenance[1] * PCT_LUBE_OIL, maintenance[2] * PCT_LUBE_OIL, maintenance[3] * PCT_LUBE_OIL]
        df.loc[6] = ['2019 Motor Oil (Household Average)', maintenance[0], maintenance[1], maintenance[2],
                     maintenance[3]]
        df.loc[len(df.index)] = ['', '', '', '', '']
        print(df)
        return df

    # Need to add the totals with the households
    def __get_food_alcohol_expenditure(self):
        """
        :return: df <pandas.DataFrame>
            A DataFrame containing the Food/Alcohol/Tobacco Expenditures part of the Demand Report
        """
        FOOD_HOME_INTERCEPT = 3217.45024906648
        FOOD_HOME_VAR_1 = 0.017166271084922
        FOOD_AWAY_INTERCEPT = 1479.12593041089
        FOOD_AWAY_VAR_1 = 0.0247768430538488
        ALCOHOL_INTERCEPT = 191.7620622831
        ALCOHOL_VAR_1 = 0.0046904313
        TOBACCO_INTERCEPT = 272.6473946058
        TOBACCO_VAR_1 = 0.002852737
        TOBACCO_VAR_2 = 0.0000000269
        PCT_RESTAURANT_MEALS = 0.845561521
        PCT_BREAKFAST = 0.106167026
        PCT_LUNCH = 0.323562559
        PCT_DINNER = 0.486586568
        PCT_ALCOHOL_HOME = 0.545958358
        PCT_ALCOHOL_AWAY = 0.454041642
        PCT_BEER = 0.151358724
        PCT_WINE = 0.063775422
        PCT_OTHER_ALCOHOL = 0.117520113
        PCT_CIGARETTES = 0.834323474
        PCT_OTHER_TOBACCO = 0.128728913
        PCT_ACCESSORIES = 0.027710709
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [],
                           '1.0-Mile Radius': [], '1.25-Mile Radius': []})
        df.loc[1] = ['2019 Food at home (Household Average)',
                     FOOD_HOME_INTERCEPT + (self.median_income[0] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[1] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[2] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[3] * FOOD_HOME_VAR_1)]
        df.loc[2] = ['2019 Food away from home (Household Average)',
                     FOOD_AWAY_INTERCEPT + (self.median_income[0] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[1] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[2] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[3] * FOOD_AWAY_VAR_1)]
        df.loc[3] = ['2019 Meals at restaurants, carry outs and other (Household Average)',
                     PCT_RESTAURANT_MEALS * df.iat[2, 1], PCT_RESTAURANT_MEALS * df.iat[2, 2],
                     PCT_RESTAURANT_MEALS * df.iat[2, 3], PCT_RESTAURANT_MEALS * df.iat[2, 4]]
        df.loc[4] = ['2019 Breakfast and brunch (Household Average)', PCT_BREAKFAST * df.iat[2, 1],
                     PCT_BREAKFAST * df.iat[2, 2], PCT_BREAKFAST * df.iat[2, 3], PCT_BREAKFAST * df.iat[2, 4]]
        df.loc[5] = ['2019 Lunch (Household Average)', PCT_LUNCH * df.iat[2, 1], PCT_LUNCH * df.iat[2, 2],
                     PCT_LUNCH * df.iat[2, 3], PCT_LUNCH * df.iat[2, 4]]
        df.loc[6] = ['2019 Dinner (Household Average)', PCT_DINNER * df.iat[2, 1], PCT_DINNER * df.iat[2, 2],
                     PCT_DINNER * df.iat[2, 3], PCT_DINNER * df.iat[2, 4]]
        df.loc[8] = ['2019 Alcoholic Beverages (Household Average)',
                     ALCOHOL_INTERCEPT + (self.median_income[0] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[1] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[2] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[3] * ALCOHOL_VAR_1)]
        df.loc[9] = ['2019 At Home (Household Average)', PCT_ALCOHOL_HOME * df.iat[8, 1],
                     PCT_ALCOHOL_HOME * df.iat[8, 2], PCT_ALCOHOL_HOME * df.iat[8, 3], PCT_ALCOHOL_HOME * df.iat[8, 4]]
        df.loc[10] = ['2019 Away from Home (Household Average)', PCT_ALCOHOL_AWAY * df.iat[8, 1],
                      PCT_ALCOHOL_AWAY * df.iat[8, 2], PCT_ALCOHOL_AWAY * df.iat[8, 3], PCT_ALCOHOL_AWAY * df.iat[8, 4]]
        df.loc[12] = ['2019 Beer and ale (Household Average)', PCT_BEER * df.iat[8, 1], PCT_BEER * df.iat[8, 2],
                      PCT_BEER * df.iat[8, 3], PCT_BEER * df.iat[8, 4]]
        df.loc[14] = ['2019 Wine (Household Average)', PCT_WINE * df.iat[8, 1], PCT_WINE * df.iat[8, 2],
                      PCT_WINE * df.iat[8, 3], PCT_WINE * df.iat[8, 4]]
        df.loc[16] = ['2019 Other Alcoholic Beverages (Household Average)', PCT_OTHER_ALCOHOL * df.iat[8, 1],
                      PCT_OTHER_ALCOHOL * df.iat[8, 2], PCT_OTHER_ALCOHOL * df.iat[8, 3],
                      PCT_OTHER_ALCOHOL * df.iat[8, 4]]
        tobacco = [(self.median_income[0] * TOBACCO_VAR_1) - (self.median_income[0] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[1] * TOBACCO_VAR_1) - (self.median_income[1] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[2] * TOBACCO_VAR_1) - (self.median_income[2] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[3] * TOBACCO_VAR_1) - (self.median_income[3] ** 2 * TOBACCO_VAR_2)]
        df.loc[18] = ['2019 Tobacco products and smoking supplies (Household Average)', TOBACCO_INTERCEPT + tobacco[0],
                      TOBACCO_INTERCEPT + tobacco[1], TOBACCO_INTERCEPT + tobacco[2], TOBACCO_INTERCEPT + tobacco[3]]
        df.loc[20] = ['2019 Cigarettes (Household Average)', PCT_CIGARETTES * df.iat[18, 1],
                      PCT_CIGARETTES * df.iat[18, 2], PCT_CIGARETTES * df.iat[18, 3], PCT_CIGARETTES * df.iat[18, 4]]
        df.loc[22] = ['2019 Other Tobacco Products (Household Average)', PCT_OTHER_TOBACCO * df.iat[18, 1],
                      PCT_OTHER_TOBACCO * df.iat[18, 2], PCT_OTHER_TOBACCO * df.iat[18, 3],
                      PCT_OTHER_TOBACCO * df.iat[18, 4]]
        df.loc[24] = ['2019 Smoking Accessories (Household Average)', PCT_ACCESSORIES * df.iat[18, 1],
                      PCT_ACCESSORIES * df.iat[18, 2], PCT_ACCESSORIES * df.iat[18, 3], PCT_ACCESSORIES * df.iat[18, 4]]


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    location_address = input('Enter the Address for which you would like your report: \n')
    location_coordinates = get_lat_long(location_address)
    # location_2000_acs = get_2000_caps(location_coordinates)

    required_data = CAPSData(location_coordinates)
    location_acs_table = required_data.get_caps()
    location_af_table = required_data.get_af_table()
    for row in location_af_table.iterrows():
        print(row)
    required_data.close()
    report = Reports(location_acs_table)
    # get_race_ethnicity(location_acs_table)
