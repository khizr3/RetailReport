"""
This is a helper file that creates a DataSources object with loaded data stored as object variables

Author: Khizr Ali Khizr89@gmail.com

Created: June 9th, 2022
"""
# Imports
import data_source
import pandas as pd  # Using DataFrames to store and manipulate data


class _Reports:
    def __init__(self, location_address):
        acs_data = data_source.ACSData(location_address)

        self.acs_data_current = acs_data.get_current_caps()

        self.af_table_2010 = acs_data.get_2010_af_table()
        self.af_table_current = acs_data.get_current_af_table()

        self.pop_hh_2000 = acs_data.get_2000_pop_hh()

        acs_data.quit_drivers()

        self.census_report_2010 = data_source.get_2010_census_caps()
        self.census_report_current = data_source.get_2020_census_caps()

        self.combined_data = self.get_combined_data()

    def get_combined_data(self):
        df = pd.DataFrame({'2010 Pop': [], '2010 HH': [], '2010 WCollar': [], '2010 BCollar': [], '2010 Median Inc': [],
                           '2010 Mean Inc': [], '2020 Pop': [], '2020 HH': [], '2020 WCollar': [], '2020 BCollar': [],
                           '2020 Median Inc': [], '2020 Mean Inc': []})
        for radius in [0.5, 0.75, 1, 1.25]:
            data_2010 = [0, 0, 0, 0, 0, 0]
            data_current = [0, 0, 0, 0, 0, 0]
            radius_pop_2010 = self.af_table_2010[self.af_table_2010['Radius'] == radius]
            radius_pop_current = self.af_table_current[self.af_table_current['Radius'] == radius]
            total_pop_2010 = radius_pop_2010['Total population'].sum()
            total_pop_current = radius_pop_current['Total population'].sum()
            print(len(radius_pop_2010), len(radius_pop_current))
            for row in radius_pop_2010.itertuples():
                percent_total = row[3] / total_pop_2010
                tract_row = self.census_report_2010.loc[self.census_report_2010['TractNumber'] == row[1]]
                data_2010[0] += percent_total * float(tract_row['Total population'].values[0])
                data_2010[1] += percent_total * float(tract_row['Total households'].values[0])
                data_2010[2] += percent_total * float(tract_row['PCT WHITE COLLAR'].values[0])
                data_2010[3] += percent_total * float(tract_row['PCT BLUE COLLAR'].values[0])
                data_2010[4] += percent_total * float(tract_row['Median income'].values[0])
                data_2010[5] += percent_total * float(tract_row['Mean income'].values[0])
            for row in radius_pop_current.itertuples():
                percent_total = row[3] / total_pop_current
                tract_row = self.census_report_current.loc[self.census_report_current['TractNumber'] == row[1]]
                print(tract_row.columns)
                data_current[0] += percent_total * float(tract_row['Total population'].values[0])
                data_current[1] += percent_total * float(tract_row['Total households'].values[0])
                data_current[2] += percent_total * float(tract_row['PCT WHITE COLLAR'].values[0])
                data_current[3] += percent_total * float(tract_row['PCT BLUE COLLAR'].values[0])
                data_current[4] += percent_total * float(tract_row['Median income'].values[0])
                data_current[5] += percent_total * float(tract_row['Mean income'].values[0])
            df.loc[len(df.index)] = data_2010 + data_current
        return df


class DemandReport(_Reports):
    # Initialization method to get the required coordinates data
    def __init__(self, location_address):
        super().__init__(location_address)
        """
        
        # self.__get_automotive_expenditure()
        self.__get_occupation()
        """

    def get_demand_report(self):
        """
        Necessary Categories:
        Population Trend and Density: 2010 Data, CURRENT CAPS, future projections
        Households Trend: 2000 Households 2010 Data, CURRENT CAPS, future projections
        Income: 2010 Data, CURRENT CAPS, future projections
        Household Vehicles: CURRENT CAPS
        Race & Ethnicity: COMPLETE
        Education and Occupation: COMPLETE
        Age and Occupancy: CURRENT CAPS
        Retail Sales Potential: CURRENT CAPS
        Household Expenditure: CURRENT CAPS
        :return:
        """
        # trade_area = pd.DataFrame()
        population_density = self.__get_population_density()
        household_trend = self.__get_household_trend()
        income = self.__get_income()
        race_ethnicity = self.__get_race_ethnicity()
        education = self.__get_education()
        occupation = self.__get_occupation()
        age_occupancy = self.__get_age_occupancy()
        sales_potential_expenditure = self.__get_sales_potential_expenditure()
        # trade_area = pd.concat(trade_area, ['POPULATION TREND', '', '', ''])

    def __get_population_density(self):
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['POPULATION TREND', '', '', '', '']
        df.loc[1] = ['2010 Total Population',
                     self.combined_data['2010 Pop'][0],
                     self.combined_data['2010 Pop'][1],
                     self.combined_data['2010 Pop'][2],
                     self.combined_data['2010 Pop'][3]]
        df.loc[2] = ['2020 Total Population',
                     self.combined_data['2020 Pop'][0],
                     self.combined_data['2020 Pop'][1],
                     self.combined_data['2020 Pop'][2],
                     self.combined_data['2020 Pop'][3]]
        df.loc[3] = ['2024 Total Population', '', '', '', '']
        df.loc[4] = ['  % Population Change 2000 to 2010',
                     (df.iat[1, 1] - self.pop_hh_2000[0][0]) / self.pop_hh_2000[0][0] * 100,
                     (df.iat[1, 2] - self.pop_hh_2000[1][0]) / self.pop_hh_2000[1][0] * 100,
                     (df.iat[1, 3] - self.pop_hh_2000[2][0]) / self.pop_hh_2000[2][0] * 100,
                     (df.iat[1, 4] - self.pop_hh_2000[3][0]) / self.pop_hh_2000[3][0] * 100]
        df.loc[5] = ['  % Population Change 2000 to 2020',
                     (df.iat[2, 1] - self.pop_hh_2000[0][0]) / self.pop_hh_2000[0][0] * 100,
                     (df.iat[2, 2] - self.pop_hh_2000[1][0]) / self.pop_hh_2000[1][0] * 100,
                     (df.iat[2, 3] - self.pop_hh_2000[2][0]) / self.pop_hh_2000[2][0] * 100,
                     (df.iat[2, 4] - self.pop_hh_2000[3][0]) / self.pop_hh_2000[3][0] * 100]
        df.loc[6] = ['  % Population Change 2010 to 2024', '', '', '', '']
        df.loc[7] = ['  % Population Change 2020 to 2024', '', '', '', '']
        df.loc[8] = ['', '', '', '', '']
        df.loc[9] = ['2019 Total Daytime Population', '', '', '', '']
        df.loc[10] = ['2019 Total Employees', '', '', '', '']
        df.loc[11] = ['2019 Total Daytime at Home Population', '', '', '', '']
        df.loc[12] = ['2019 Total Employees (% of Daytime Population)', '', '', '', '']
        df.loc[13] = ['2019 Total Daytime at Home Population (% of Daytime Population)', '', '', '', '']
        df.loc[14] = ['', '', '', '', '']
        df.loc[15] = ['DENSITY', '', '', '', '']
        df.loc[16] = ['2020 Population Density',
                      df.iat[2, 1] / 0.79,
                      df.iat[2, 2] / 1.77,
                      df.iat[2, 3] / 3.14,
                      df.iat[2, 4] / 4.91]
        df.loc[17] = ['2020 Employee Density', '', '', '', '']
        df.loc[18] = ['', '', '', '', '']

        return df

    def __get_household_trend(self):
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['HOUSEHOLDS TREND', '', '', '', '']
        df.loc[1] = ['2010 Households',
                     self.combined_data['2010 HH'][0],
                     self.combined_data['2010 HH'][1],
                     self.combined_data['2010 HH'][2],
                     self.combined_data['2010 HH'][3]]
        df.loc[2] = ['2020 Households',
                     self.combined_data['2020 HH'][0],
                     self.combined_data['2020 HH'][1],
                     self.combined_data['2020 HH'][2],
                     self.combined_data['2020 HH'][3]]
        df.loc[3] = ['2024 Households', '', '', '', '']
        df.loc[4] = ['  % Household Change 2000 to 2010',
                     (df.iat[1, 1] - self.pop_hh_2000[0][1]) / self.pop_hh_2000[0][1] * 100,
                     (df.iat[1, 2] - self.pop_hh_2000[1][1]) / self.pop_hh_2000[1][1] * 100,
                     (df.iat[1, 3] - self.pop_hh_2000[2][1]) / self.pop_hh_2000[2][1] * 100,
                     (df.iat[1, 4] - self.pop_hh_2000[3][1]) / self.pop_hh_2000[3][1] * 100]
        df.loc[5] = ['  % Household Change 2000 to 2020',
                     (df.iat[2, 1] - self.pop_hh_2000[0][1]) / self.pop_hh_2000[0][1] * 100,
                     (df.iat[2, 2] - self.pop_hh_2000[1][1]) / self.pop_hh_2000[1][1] * 100,
                     (df.iat[2, 3] - self.pop_hh_2000[2][1]) / self.pop_hh_2000[2][1] * 100,
                     (df.iat[2, 4] - self.pop_hh_2000[3][1]) / self.pop_hh_2000[3][1] * 100]
        df.loc[6] = ['  % Household Change 2010 to 2024', '', '', '', '']
        df.loc[7] = ['  % Household Change 2020 to 2024', '', '', '', '']
        df.loc[8] = ['', '', '', '', '']
        df.loc[9] = ['2020 Average household size: Owner occupied',
                     self.acs_data_current['AvgOwnerHHSize'][0],
                     self.acs_data_current['AvgOwnerHHSize'][1],
                     self.acs_data_current['AvgOwnerHHSize'][2],
                     self.acs_data_current['AvgOwnerHHSize'][3]]
        df.loc[10] = ['2020 Average household size: Renter occupied',
                      self.acs_data_current['AvgRenterHHSize'][0],
                      self.acs_data_current['AvgRenterHHSize'][1],
                      self.acs_data_current['AvgRenterHHSize'][2],
                      self.acs_data_current['AvgRenterHHSize'][3]]
        df.loc[11] = ['', '', '', '', '']

        return df

    def __get_income(self):
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['INCOME', '', '', '', '']
        df.loc[1] = ['2010 Household income: Median',
                     self.combined_data['2010 Median Inc'][0],
                     self.combined_data['2010 Median Inc'][1],
                     self.combined_data['2010 Median Inc'][2],
                     self.combined_data['2010 Median Inc'][3]]
        df.loc[2] = ['2010 Household income: Average',
                     self.combined_data['2010 Mean Inc'][0],
                     self.combined_data['2010 Mean Inc'][1],
                     self.combined_data['2010 Mean Inc'][2],
                     self.combined_data['2010 Mean Inc'][3]]
        df.loc[3] = ['', '', '', '']
        df.loc[4] = ['2020 Household income: Median',
                     self.combined_data['2020 Median Inc'][0],
                     self.combined_data['2020 Median Inc'][1],
                     self.combined_data['2020 Median Inc'][2],
                     self.combined_data['2020 Median Inc'][3]]
        df.loc[5] = ['2020 Household income: Average',
                     self.combined_data['2020 Mean Inc'][0],
                     self.combined_data['2020 Mean Inc'][1],
                     self.combined_data['2020 Mean Inc'][2],
                     self.combined_data['2020 Mean Inc'][3]]
        df.loc[6] = ['', '', '', '']
        df.loc[7] = ['2024 Household income: Median', '', '', '', '']
        df.loc[8] = ['2024 Household income: Average', '', '', '', '']
        df.loc[9] = ['', '', '', '']

        return df

    def __get_household_vehicles(self):
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['HOUSEHOLD VEHICLES', '', '', '', '']
        vehicle_1 = self.acs_data_current['Vehicles1']
        vehicle_2 = 2 * self.acs_data_current['Vehicles2']
        vehicles_GE3 = 3.2 * self.acs_data_current['VehiclesGE3']
        df.loc[1] = ['2020 Households: Number of vehicles available',
                     vehicle_1[0] + vehicle_2[0] + vehicles_GE3[0],
                     vehicle_1[1] + vehicle_2[1] + vehicles_GE3[1],
                     vehicle_1[2] + vehicle_2[2] + vehicles_GE3[2],
                     vehicle_1[2] + vehicle_2[2] + vehicles_GE3[2]]
        df.loc[2] = ['2020 Owner occupied: Number of vehicles available',
                     self.current_acs['pctOwnerOcc'][0] * df.iat[1, 1],
                     self.current_acs['pctOwnerOcc'][1] * df.iat[1, 2],
                     self.current_acs['pctOwnerOcc'][2] * df.iat[1, 3],
                     self.current_acs['pctOwnerOcc'][3] * df.iat[1, 4]]
        df.loc[3] = ['2020 Renter occupied: Number of vehicles available',
                     self.current_acs['pctRenterOcc'][0] * df.iat[1, 1],
                     self.current_acs['pctRenterOcc'][1] * df.iat[1, 2],
                     self.current_acs['pctRenterOcc'][2] * df.iat[1, 3],
                     self.current_acs['pctRenterOcc'][3] * df.iat[1, 4]]
        df.loc[4] = ['', '', '', '']

    def __get_race_ethnicity(self):
        """
        :return: df <pandas.DataFrame>
            A DataFrame containing the Race & Ethnicity part of the Demand Report
        """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['RACE & ETHNICITY', '', '', '', '']
        df.loc[1] = ['% 2019 White Alone',
                     self.acs_data_current['pctWhite1'][0],
                     self.acs_data_current['pctWhite1'][1],
                     self.acs_data_current['pctWhite1'][2],
                     self.acs_data_current['pctWhite1'][3]]
        df.loc[2] = ['% 2019 Black or African American Alone',
                     self.acs_data_current['pctBlack1'][0],
                     self.acs_data_current['pctBlack1'][1],
                     self.acs_data_current['pctBlack1'][2],
                     self.acs_data_current['pctBlack1'][3]]
        df.loc[3] = ['% 2019 American Indian and Alaska Native Alone',
                     self.acs_data_current['pctIndian1'][0],
                     self.acs_data_current['pctIndian1'][1],
                     self.acs_data_current['pctIndian1'][2],
                     self.acs_data_current['pctIndian1'][3]]
        df.loc[4] = ['% 2019 Asian Alone',
                     self.acs_data_current['pctAsian1'][0],
                     self.acs_data_current['pctAsian1'][1],
                     self.acs_data_current['pctAsian1'][2],
                     self.acs_data_current['pctAsian1'][3]]
        df.loc[5] = ['% 2019 Native Hawaiian and OPI alone',
                     self.acs_data_current['pctHawnPI1'][0],
                     self.acs_data_current['pctHawnPI1'][1],
                     self.acs_data_current['pctHawnPI1'][2],
                     self.acs_data_current['pctHawnPI1'][3]]
        df.loc[6] = ['% 2019 Some Other Race alone',
                     self.acs_data_current['pctOther1'][0],
                     self.acs_data_current['pctOther1'][1],
                     self.acs_data_current['pctOther1'][2],
                     self.acs_data_current['pctOther1'][3]]
        df.loc[7] = ['% 2019 Two or More Races',
                     self.acs_data_current['pctMultiRace'][0],
                     self.acs_data_current['pctMultiRace'][1],
                     self.acs_data_current['pctMultiRace'][2],
                     self.acs_data_current['pctMultiRace'][3]]
        df.loc[8] = ['', '', '', '', '']
        df.loc[9] = ['% 2019 Hispanic',
                     self.acs_data_current['pctHispanicPop'][0],
                     self.acs_data_current['pctHispanicPop'][1],
                     self.acs_data_current['pctHispanicPop'][2],
                     self.acs_data_current['pctHispanicPop'][3]]
        df.loc[10] = ['% 2019 Not Hispanic',
                      self.acs_data_current['pctNonHispPop'][0],
                      self.acs_data_current['pctNonHispPop'][1],
                      self.acs_data_current['pctNonHispPop'][2],
                      self.acs_data_current['pctNonHispPop'][3]]
        df.loc[11] = ['', '', '', '', '']
        print('Race and Ethnicity Values Completed')
        return df

    def __get_education(self):
        """
                :return: df <pandas.DataFrame>
                    A DataFrame containing the Race & Ethnicity part of the Demand Report
                """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['EDUCATION & OCCUPATION', '', '', '', '']
        df.loc[1] = ['EDUCATION', '', '', '', '']
        df.loc[2] = ['% 2019 No High School Diploma',
                     self.acs_data_current['pctLessThan9th'][0] + self.acs_data_current['pctSomeHighSchool'][0],
                     self.acs_data_current['pctLessThan9th'][1] + self.acs_data_current['pctSomeHighSchool'][1],
                     self.acs_data_current['pctLessThan9th'][2] + self.acs_data_current['pctSomeHighSchool'][2],
                     self.acs_data_current['pctLessThan9th'][3] + self.acs_data_current['pctSomeHighSchool'][3]]
        df.loc[3] = ['% 2019 High school graduate, GED, or alternative',
                     self.acs_data_current['pctHighSchool'][0],
                     self.acs_data_current['pctHighSchool'][1],
                     self.acs_data_current['pctHighSchool'][2],
                     self.acs_data_current['pctHighSchool'][3]]
        df.loc[4] = ['% 2019 College No Degree',
                     self.acs_data_current['pctSomeCollege'][0],
                     self.acs_data_current['pctSomeCollege'][1],
                     self.acs_data_current['pctSomeCollege'][2],
                     self.acs_data_current['pctSomeCollege'][3]]
        df.loc[5] = ['% 2019 College Degree',
                     self.acs_data_current['pctAssociates'][0] + self.acs_data_current['pctBachelors'][0],
                     self.acs_data_current['pctAssociates'][1] + self.acs_data_current['pctBachelors'][1],
                     self.acs_data_current['pctAssociates'][2] + self.acs_data_current['pctBachelors'][2],
                     self.acs_data_current['pctAssociates'][3] + self.acs_data_current['pctBachelors'][3]]
        df.loc[6] = ['% 2019 Advanced Degree',
                     self.acs_data_current['pctGradProf'][0],
                     self.acs_data_current['pctGradProf'][1],
                     self.acs_data_current['pctGradProf'][2],
                     self.acs_data_current['pctGradProf'][3]]
        df.loc[7] = ['% 2019 College or Advanced Degree',
                     df.iat[5, 1] + df.iat[6, 1],
                     df.iat[5, 2] + df.iat[6, 2],
                     df.iat[5, 3] + df.iat[6, 3],
                     df.iat[5, 4] + df.iat[6, 4]]
        df.loc[8] = ['', '', '', '', '']
        return df

    def __get_occupation(self):
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['OCCUPATION', '', '', '', '']
        blue_collar_by_radius = []
        white_collar_by_radius = []
        df.loc[1] = ['% 2010 Occupation: White collar',
                     white_collar_by_radius[0],
                     white_collar_by_radius[1],
                     white_collar_by_radius[2],
                     white_collar_by_radius[3]]
        df.loc[2] = ['% 2010 Occupation: Blue collar',
                     blue_collar_by_radius[0],
                     blue_collar_by_radius[1],
                     blue_collar_by_radius[2],
                     blue_collar_by_radius[3]]
        df.loc[3] = ['% 2019 Occupation: White collar',
                     self.current_acs['pctManProfOccs'][0] + self.current_acs['pctSalesOffOccs'][0],
                     self.current_acs['pctManProfOccs'][1] + self.current_acs['pctSalesOffOccs'][1],
                     self.current_acs['pctManProfOccs'][2] + self.current_acs['pctSalesOffOccs'][2],
                     self.current_acs['pctManProfOccs'][3] + self.current_acs['pctSalesOffOccs'][3]]
        df.loc[4] = ['% 2019 Occupation: Blue collar',
                     100 - df.iat[3, 1],
                     100 - df.iat[3, 2],
                     100 - df.iat[3, 3],
                     100 - df.iat[3, 4]]
        return df

    def __get_age_occupancy(self):
        """
        :return: df <pandas.DataFrame>
            A DataFrame containing the Race & Ethnicity part of the Demand Report
        """
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['AGE & OCCUPANCY', '', '', '', '']
        df.loc[1] = ['AGE', '', '', '', '']
        df.loc[2] = ['% 2019 Total Population: Median Age',
                     self.current_acs['MedianAge'][0],
                     self.current_acs['MedianAge'][1],
                     self.current_acs['MedianAge'][2],
                     self.current_acs['MedianAge'][3]]
        df.loc[3] = ['', '', '', '', '']
        df.loc[4] = ['OCCUPANCY', '', '', '', '']
        df.loc[5] = ['2019 Households',
                     self.current_acs['TotHHs'][0],
                     self.current_acs['TotHHs'][1],
                     self.current_acs['TotHHs'][2],
                     self.current_acs['TotHHs'][3]]
        df.loc[6] = ['% 2019 Owner Occupied Housing Units',
                     self.current_acs['pctOwnerOcc'][0],
                     self.current_acs['pctOwnerOcc'][1],
                     self.current_acs['pctOwnerOcc'][2],
                     self.current_acs['pctOwnerOcc'][3]]
        df.loc[7] = ['% 2019 Renter Occupied Housing Units',
                     self.current_acs['pctRenterOcc'][0],
                     self.current_acs['pctRenterOcc'][1],
                     self.current_acs['pctRenterOcc'][2],
                     self.current_acs['pctRenterOcc'][3]]
        df.loc[8] = ['', '', '', '', '']
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
        df.loc[1] = ['2019 Gasoline (Household Average)',
                     df.iat[0, 1] * PCT_GASOLINE,
                     df.iat[0, 2] * PCT_GASOLINE,
                     df.iat[0, 3] * PCT_GASOLINE,
                     df.iat[0, 4] * PCT_GASOLINE]
        df.loc[2] = ['2019 Diesel Fuel (Household Average)',
                     df.iat[0, 1] * PCT_DIESEL,
                     df.iat[0, 2] * PCT_DIESEL,
                     df.iat[0, 3] * PCT_DIESEL,
                     df.iat[0, 4] * PCT_DIESEL]
        df.loc[3] = ['2019 Gasoline on out-of-town trips (Household Average)',
                     df.iat[0, 1] * PCT_GASOLINE_OOT,
                     df.iat[0, 2] * PCT_GASOLINE_OOT,
                     df.iat[0, 3] * PCT_GASOLINE_OOT,
                     df.iat[0, 4] * PCT_GASOLINE_OOT]
        df.loc[4] = ['2019 Motor Oil (Household Average)',
                     df.iat[0, 1] * PCT_MOTOR_OIL,
                     df.iat[0, 2] * PCT_MOTOR_OIL,
                     df.iat[0, 3] * PCT_MOTOR_OIL,
                     df.iat[0, 4] * PCT_MOTOR_OIL]
        maintenance = [(self.median_income[0] * MAINTENANCE_VAR_1) - (self.median_income[0] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[1] * MAINTENANCE_VAR_1) - (self.median_income[1] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[2] * MAINTENANCE_VAR_1) - (self.median_income[2] ** 2 * MAINTENANCE_VAR_2),
                       (self.median_income[3] * MAINTENANCE_VAR_1) - (self.median_income[3] ** 2 * MAINTENANCE_VAR_2)]
        for index, val in enumerate(maintenance):
            maintenance[index] = MAINTENANCE_INTERCEPT + val
        df.loc[5] = ['2019 Lube, oil change, and oil filters (Household Average)',
                     maintenance[0] * PCT_LUBE_OIL,
                     maintenance[1] * PCT_LUBE_OIL,
                     maintenance[2] * PCT_LUBE_OIL,
                     maintenance[3] * PCT_LUBE_OIL]
        df.loc[6] = ['2019 Maintenance and Repairs (Household Average)',
                     maintenance[0],
                     maintenance[1],
                     maintenance[2],
                     maintenance[3]]
        df.loc[len(df.index)] = ['', '', '', '', '']
        return df

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
        households = [self.combined_data['2020 HH'][0],
                      self.combined_data['2020 HH'][1],
                      self.combined_data['2020 HH'][2],
                      self.combined_data['2020 HH'][3]]
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [],
                           '1.0-Mile Radius': [], '1.25-Mile Radius': []})
        df.loc[1] = ['2019 Food at home (Household Average)',
                     FOOD_HOME_INTERCEPT + (self.median_income[0] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[1] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[2] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[3] * FOOD_HOME_VAR_1)]
        df.loc[0] = ['2019 Food at home',
                     df.iat[1, 1] * households[0],
                     df.iat[1, 2] * households[1],
                     df.iat[1, 3] * households[2],
                     df.iat[1, 4] * households[3]]
        df.loc[2] = ['2019 Food away from home (Household Average)',
                     FOOD_AWAY_INTERCEPT + (self.median_income[0] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[1] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[2] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[3] * FOOD_AWAY_VAR_1)]
        df.loc[3] = ['2019 Meals at restaurants, carry outs and other (Household Average)',
                     PCT_RESTAURANT_MEALS * df.iat[2, 1],
                     PCT_RESTAURANT_MEALS * df.iat[2, 2],
                     PCT_RESTAURANT_MEALS * df.iat[2, 3],
                     PCT_RESTAURANT_MEALS * df.iat[2, 4]]
        df.loc[4] = ['2019 Breakfast and brunch (Household Average)',
                     PCT_BREAKFAST * df.iat[2, 1],
                     PCT_BREAKFAST * df.iat[2, 2],
                     PCT_BREAKFAST * df.iat[2, 3],
                     PCT_BREAKFAST * df.iat[2, 4]]
        df.loc[5] = ['2019 Lunch (Household Average)',
                     PCT_LUNCH * df.iat[2, 1],
                     PCT_LUNCH * df.iat[2, 2],
                     PCT_LUNCH * df.iat[2, 3],
                     PCT_LUNCH * df.iat[2, 4]]
        df.loc[6] = ['2019 Dinner (Household Average)',
                     PCT_DINNER * df.iat[2, 1],
                     PCT_DINNER * df.iat[2, 2],
                     PCT_DINNER * df.iat[2, 3],
                     PCT_DINNER * df.iat[2, 4]]
        df.loc[8] = ['2019 Alcoholic Beverages (Household Average)',
                     ALCOHOL_INTERCEPT + (self.median_income[0] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[1] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[2] * ALCOHOL_VAR_1),
                     ALCOHOL_INTERCEPT + (self.median_income[3] * ALCOHOL_VAR_1)]
        df.loc[7] = ['2019 Alcoholic Beverages',
                     df.iat[8, 1] * households[0],
                     df.iat[8, 2] * households[1],
                     df.iat[8, 3] * households[2],
                     df.iat[8, 4] * households[3]]
        df.loc[9] = ['2019 At Home (Household Average)',
                     PCT_ALCOHOL_HOME * df.iat[8, 1],
                     PCT_ALCOHOL_HOME * df.iat[8, 2],
                     PCT_ALCOHOL_HOME * df.iat[8, 3],
                     PCT_ALCOHOL_HOME * df.iat[8, 4]]
        df.loc[10] = ['2019 Away from Home (Household Average)',
                      PCT_ALCOHOL_AWAY * df.iat[8, 1],
                      PCT_ALCOHOL_AWAY * df.iat[8, 2],
                      PCT_ALCOHOL_AWAY * df.iat[8, 3],
                      PCT_ALCOHOL_AWAY * df.iat[8, 4]]
        df.loc[12] = ['2019 Beer and ale (Household Average)',
                      PCT_BEER * df.iat[8, 1],
                      PCT_BEER * df.iat[8, 2],
                      PCT_BEER * df.iat[8, 3],
                      PCT_BEER * df.iat[8, 4]]
        df.loc[11] = ['2019 Beer and Ale',
                      df.iat[12, 1] * households[0],
                      df.iat[12, 2] * households[1],
                      df.iat[12, 3] * households[2],
                      df.iat[12, 4] * households[3]]
        df.loc[14] = ['2019 Wine (Household Average)',
                      PCT_WINE * df.iat[8, 1],
                      PCT_WINE * df.iat[8, 2],
                      PCT_WINE * df.iat[8, 3],
                      PCT_WINE * df.iat[8, 4]]
        df.loc[13] = ['2019 Wine',
                      df.iat[14, 1] * households[0],
                      df.iat[14, 2] * households[1],
                      df.iat[14, 3] * households[2],
                      df.iat[14, 4] * households[3]]
        df.loc[16] = ['2019 Other Alcoholic Beverages (Household Average)',
                      PCT_OTHER_ALCOHOL * df.iat[8, 1],
                      PCT_OTHER_ALCOHOL * df.iat[8, 2],
                      PCT_OTHER_ALCOHOL * df.iat[8, 3],
                      PCT_OTHER_ALCOHOL * df.iat[8, 4]]
        df.loc[15] = ['2019 Other Alcoholic Beverages',
                      df.iat[16, 1] * households[0],
                      df.iat[16, 2] * households[1],
                      df.iat[16, 3] * households[2],
                      df.iat[16, 4] * households[3]]
        tobacco = [(self.median_income[0] * TOBACCO_VAR_1) - (self.median_income[0] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[1] * TOBACCO_VAR_1) - (self.median_income[1] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[2] * TOBACCO_VAR_1) - (self.median_income[2] ** 2 * TOBACCO_VAR_2),
                   (self.median_income[3] * TOBACCO_VAR_1) - (self.median_income[3] ** 2 * TOBACCO_VAR_2)]
        df.loc[18] = ['2019 Tobacco products and smoking supplies (Household Average)',
                      TOBACCO_INTERCEPT + tobacco[0],
                      TOBACCO_INTERCEPT + tobacco[1],
                      TOBACCO_INTERCEPT + tobacco[2],
                      TOBACCO_INTERCEPT + tobacco[3]]
        df.loc[17] = ['2019 Tobacco products and smoking supplies',
                      df.iat[18, 1] * households[0],
                      df.iat[18, 2] * households[1],
                      df.iat[18, 3] * households[2],
                      df.iat[18, 4] * households[3]]
        df.loc[20] = ['2019 Cigarettes (Household Average)',
                      PCT_CIGARETTES * df.iat[18, 1],
                      PCT_CIGARETTES * df.iat[18, 2],
                      PCT_CIGARETTES * df.iat[18, 3],
                      PCT_CIGARETTES * df.iat[18, 4]]
        df.loc[19] = ['2019 Cigarettes',
                      df.iat[20, 1] * households[0],
                      df.iat[20, 2] * households[1],
                      df.iat[20, 3] * households[2],
                      df.iat[20, 4] * households[3]]
        df.loc[22] = ['2019 Other Tobacco Products (Household Average)',
                      PCT_OTHER_TOBACCO * df.iat[18, 1],
                      PCT_OTHER_TOBACCO * df.iat[18, 2],
                      PCT_OTHER_TOBACCO * df.iat[18, 3],
                      PCT_OTHER_TOBACCO * df.iat[18, 4]]
        df.loc[21] = ['2019 Other Tobacco Products',
                      df.iat[22, 1] * households[0],
                      df.iat[22, 2] * households[1],
                      df.iat[22, 3] * households[2],
                      df.iat[22, 4] * households[3]]
        df.loc[24] = ['2019 Smoking Accessories (Household Average)',
                      PCT_ACCESSORIES * df.iat[18, 1],
                      PCT_ACCESSORIES * df.iat[18, 2],
                      PCT_ACCESSORIES * df.iat[18, 3],
                      PCT_ACCESSORIES * df.iat[18, 4]]
        df.loc[23] = ['2019 Smoking Accessories',
                      df.iat[24, 1] * households[0],
                      df.iat[24, 2] * households[1],
                      df.iat[24, 3] * households[2],
                      df.iat[24, 4] * households[3]]

        return df

    def __get_sales_potential_expenditure(self):
        food_alcohol_expenditure = self.__get_food_alcohol_expenditure()
        automotive_expenditure = self.__get_automotive_expenditure()
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [],
                           '1.0-Mile Radius': [], '1.25-Mile Radius': []})
        df.loc[1] = ['2019 Food at home (Household Average)',
                     FOOD_HOME_INTERCEPT + (self.median_income[0] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[1] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[2] * FOOD_HOME_VAR_1),
                     FOOD_HOME_INTERCEPT + (self.median_income[3] * FOOD_HOME_VAR_1)]
        df.loc[0] = ['2019 Food at home',
                     df.iat[1, 1] * households[0],
                     df.iat[1, 2] * households[1],
                     df.iat[1, 3] * households[2],
                     df.iat[1, 4] * households[3]]
        df.loc[2] = ['2019 Food away from home (Household Average)',
                     FOOD_AWAY_INTERCEPT + (self.median_income[0] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[1] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[2] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (self.median_income[3] * FOOD_AWAY_VAR_1)]
