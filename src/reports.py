"""
This is a helper file that creates a DataSources object with loaded data stored as object variables

Author: Khizr Ali Khizr89@gmail.com

Created: June 9th, 2022
"""
# Imports
import data_source
import pandas as pd  # Using DataFrames to store and manipulate data


class Reports:
    def __init__(self, location_coordinates):
        acs_data = data_source.ACSData(location_coordinates)

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
                           '2010 Mean Inc': [], 'NULL': [], 'NULL1': [], '2020 Pop': [], '2020 HH': [],
                           '2020 WCollar': [], '2020 BCollar': [], '2020 Median Inc': [], '2020 Mean Inc': [],
                           '2020 Employees': [], '2020 Daytime Pop': []})
        for radius in [0.5, 0.75, 1, 1.25]:
            data_2010 = [0, 0, 0, 0, 0, 0, 0, 0]
            data_current = [0, 0, 0, 0, 0, 0, 0, 0]
            radius_pop_2010 = self.af_table_2010[self.af_table_2010['Radius'] == radius]
            radius_pop_current = self.af_table_current[self.af_table_current['Radius'] == radius]
            pop_2010 = radius_pop_2010['Total population'].sum()
            pop_current = radius_pop_current['Total population'].sum()
            for row in radius_pop_2010.itertuples():
                tract_row = self.census_report_2010.loc[self.census_report_2010['TractNumber'] == row[1]]
                af = row[3] / pop_2010
                percent_of_tract = row[3] / float(tract_row['Total population'].values[0])
                data_2010[0] += percent_of_tract * af * float(tract_row['Total population'].values[0])
                data_2010[1] += percent_of_tract * af * float(tract_row['Total households'].values[0])
                data_2010[2] += af * float(tract_row['PCT WHITE COLLAR'].values[0])
                data_2010[3] += af * float(tract_row['PCT BLUE COLLAR'].values[0])
                data_2010[4] += af * float(tract_row['Median income'].values[0])
                data_2010[5] += af * float(tract_row['Mean income'].values[0])
                data_2010[6] = 0
                data_2010[7] = 0
            for row in radius_pop_current.itertuples():
                tract_row = self.census_report_current.loc[self.census_report_current['TractNumber'] == row[1]]
                af = row[3] / pop_current
                percent_of_tract = row[3] / float(tract_row['Total population'].values[0])
                data_current[0] += percent_of_tract * af * float(tract_row['Total population'].values[0])
                data_current[1] += percent_of_tract * af * float(tract_row['Total households'].values[0])
                data_current[2] += af * float(tract_row['PCT WHITE COLLAR'].values[0])
                data_current[3] += af * float(tract_row['PCT BLUE COLLAR'].values[0])
                data_current[4] += af * float(tract_row['Median income'].values[0])
                data_current[5] += af * float(tract_row['Mean income'].values[0])
                data_current[6] += percent_of_tract * af * float(tract_row['B08604'].values[0])
                data_current[7] += percent_of_tract * af * float(tract_row['Daytime Population'].values[0])
            if radius != 0.5:
                data_current[0] += df.loc[len(df.index) - 1]['2020 Pop']
                data_current[1] += df.loc[len(df.index) - 1]['2020 HH']
                data_current[6] += df.loc[len(df.index) - 1]['2020 Employees']
                data_current[7] += df.loc[len(df.index) - 1]['2020 Daytime Pop']
            df.loc[len(df.index)] = data_2010 + data_current
        return df

    def get_demand_report(self):
        return DemandReport(self).get_demand_report()

    def get_trade_area(self):
        return TradeArea(self).get_trade_area()


class DemandReport:
    # Initialization method to get the required coordinates data
    def __init__(self, report):
        self.acs_data_current = report.acs_data_current
        self.pop_hh_2000 = report.pop_hh_2000
        self.combined_data = report.combined_data

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
        population_density = self.__get_population_density()
        household_trend = self.__get_household_trend()
        income = self.__get_income()
        race_ethnicity = self.__get_race_ethnicity()
        education = self.__get_education()
        occupation = self.__get_occupation()
        age_occupancy = self.__get_age_occupancy()
        sales_potential_expenditure = self.__get_sales_potential_expenditure()
        demand_report = pd.concat([population_density,
                                   household_trend,
                                   income,
                                   race_ethnicity,
                                   education,
                                   occupation,
                                   age_occupancy,
                                   sales_potential_expenditure])

        return demand_report

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
        df.loc[9] = ['2019 Total Daytime Population',
                     self.combined_data['2020 Daytime Pop'][0],
                     self.combined_data['2020 Daytime Pop'][1],
                     self.combined_data['2020 Daytime Pop'][2],
                     self.combined_data['2020 Daytime Pop'][3]]
        df.loc[10] = ['2019 Total Employees',
                      self.combined_data['2020 Employees'][0],
                      self.combined_data['2020 Employees'][1],
                      self.combined_data['2020 Employees'][2],
                      self.combined_data['2020 Employees'][3]]
        df.loc[11] = ['2019 Total Daytime at Home Population',
                      df.iat[9, 1] - df.iat[10, 1],
                      df.iat[9, 2] - df.iat[10, 2],
                      df.iat[9, 3] - df.iat[10, 3],
                      df.iat[9, 4] - df.iat[10, 4]]
        df.loc[12] = ['2019 Total Employees (% of Daytime Population)',
                      df.iat[10, 1] / df.iat[9, 1] * 100,
                      df.iat[10, 2] / df.iat[9, 2] * 100,
                      df.iat[10, 3] / df.iat[9, 3] * 100,
                      df.iat[10, 4] / df.iat[9, 4] * 100]
        df.loc[13] = ['2019 Total Daytime at Home Population (% of Daytime Population)',
                      df.iat[11, 1] / df.iat[9, 1] * 100,
                      df.iat[11, 2] / df.iat[9, 2] * 100,
                      df.iat[11, 3] / df.iat[9, 3] * 100,
                      df.iat[11, 4] / df.iat[9, 4] * 100]
        df.loc[14] = ['', '', '', '', '']
        df.loc[15] = ['DENSITY', '', '', '', '']
        df.loc[16] = ['2020 Population Density',
                      df.iat[2, 1] / 0.79,
                      df.iat[2, 2] / 1.77,
                      df.iat[2, 3] / 3.14,
                      df.iat[2, 4] / 4.91]
        df.loc[17] = ['2020 Employee Density',
                      df.iat[12, 1] / 0.79,
                      df.iat[12, 2] / 1.77,
                      df.iat[12, 3] / 3.14,
                      df.iat[12, 4] / 4.91]
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
        df.loc[3] = ['', '', '', '', '']
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
        df.loc[6] = ['', '', '', '', '']
        df.loc[7] = ['2024 Household income: Median', '', '', '', '']
        df.loc[8] = ['2024 Household income: Average', '', '', '', '']
        df.loc[9] = ['', '', '', '', '']

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
        df.loc[1] = ['% 2010 Occupation: White collar',
                     self.combined_data['2010 WCollar'][0],
                     self.combined_data['2010 WCollar'][1],
                     self.combined_data['2010 WCollar'][2],
                     self.combined_data['2010 WCollar'][3]]
        df.loc[2] = ['% 2010 Occupation: Blue collar',
                     self.combined_data['2010 BCollar'][0],
                     self.combined_data['2010 BCollar'][1],
                     self.combined_data['2010 BCollar'][2],
                     self.combined_data['2010 BCollar'][3]]
        df.loc[3] = ['% 2019 Occupation: White collar',
                     self.acs_data_current['pctManProfOccs'][0] + self.acs_data_current['pctSalesOffOccs'][0],
                     self.acs_data_current['pctManProfOccs'][1] + self.acs_data_current['pctSalesOffOccs'][1],
                     self.acs_data_current['pctManProfOccs'][2] + self.acs_data_current['pctSalesOffOccs'][2],
                     self.acs_data_current['pctManProfOccs'][3] + self.acs_data_current['pctSalesOffOccs'][3]]
        df.loc[4] = ['% 2019 Occupation: Blue collar',
                     100 - df.iat[3, 1],
                     100 - df.iat[3, 2],
                     100 - df.iat[3, 3],
                     100 - df.iat[3, 4]]
        df.loc[5] = ['', '', '', '', '']
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
                     self.acs_data_current['MedianAge'][0],
                     self.acs_data_current['MedianAge'][1],
                     self.acs_data_current['MedianAge'][2],
                     self.acs_data_current['MedianAge'][3]]
        df.loc[3] = ['', '', '', '', '']
        df.loc[4] = ['OCCUPANCY', '', '', '', '']
        df.loc[5] = ['2019 Households',
                     self.combined_data['2020 HH'][0],
                     self.combined_data['2020 HH'][1],
                     self.combined_data['2020 HH'][2],
                     self.combined_data['2020 HH'][3]]
        df.loc[6] = ['% 2019 Owner Occupied Housing Units',
                     self.acs_data_current['pctOwnerOcc'][0],
                     self.acs_data_current['pctOwnerOcc'][1],
                     self.acs_data_current['pctOwnerOcc'][2],
                     self.acs_data_current['pctOwnerOcc'][3]]
        df.loc[7] = ['% 2019 Renter Occupied Housing Units',
                     self.acs_data_current['pctRenterOcc'][0],
                     self.acs_data_current['pctRenterOcc'][1],
                     self.acs_data_current['pctRenterOcc'][2],
                     self.acs_data_current['pctRenterOcc'][3]]
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
        median_income = [self.combined_data['2020 Median Inc'][0],
                         self.combined_data['2020 Median Inc'][1],
                         self.combined_data['2020 Median Inc'][2],
                         self.combined_data['2020 Median Inc'][3]]
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [], '1.0-Mile Radius': [],
                           '1.25-Mile Radius': []})
        df.loc[0] = ['AUTOMOTIVE',
                     AUTO_INTERCEPT + (median_income[0] * AUTO_VAR_1) - (median_income[0] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (median_income[1] * AUTO_VAR_1) - (median_income[1] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (median_income[2] * AUTO_VAR_1) - (median_income[2] ** 2. * AUTO_VAR_2),
                     AUTO_INTERCEPT + (median_income[3] * AUTO_VAR_1) - (median_income[3] ** 2. * AUTO_VAR_2)]
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
        maintenance = [(median_income[0] * MAINTENANCE_VAR_1) - (median_income[0] ** 2 * MAINTENANCE_VAR_2),
                       (median_income[1] * MAINTENANCE_VAR_1) - (median_income[1] ** 2 * MAINTENANCE_VAR_2),
                       (median_income[2] * MAINTENANCE_VAR_1) - (median_income[2] ** 2 * MAINTENANCE_VAR_2),
                       (median_income[3] * MAINTENANCE_VAR_1) - (median_income[3] ** 2 * MAINTENANCE_VAR_2)]
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
        TOBACCO_INTERCEPT = 259.05675802023478
        TOBACCO_VAR_1 = 0.0039486735202233121
        TOBACCO_VAR_2 = -0.000000047432835935931843
        TOBACCO_VAR_3 = 1.7766697338070551e-013
        TOBACCO_VAR_4 = -2.1917172106300310e-019
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
        median_income = [self.combined_data['2020 Median Inc'][0],
                         self.combined_data['2020 Median Inc'][1],
                         self.combined_data['2020 Median Inc'][2],
                         self.combined_data['2020 Median Inc'][3]]
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [],
                           '1.0-Mile Radius': [], '1.25-Mile Radius': []})
        food_at_home = [FOOD_HOME_INTERCEPT + (median_income[0] * FOOD_HOME_VAR_1),
                        FOOD_HOME_INTERCEPT + (median_income[1] * FOOD_HOME_VAR_1),
                        FOOD_HOME_INTERCEPT + (median_income[2] * FOOD_HOME_VAR_1),
                        FOOD_HOME_INTERCEPT + (median_income[3] * FOOD_HOME_VAR_1)]
        df.loc[0] = ['2019 Food at home',
                     food_at_home[0] * households[0],
                     food_at_home[1] * households[1],
                     food_at_home[2] * households[2],
                     food_at_home[3] * households[3]]
        df.loc[1] = ['2019 Food at home (Household Average)',
                     food_at_home[0],
                     food_at_home[1],
                     food_at_home[2],
                     food_at_home[3]]
        df.loc[2] = ['2019 Food away from home (Household Average)',
                     FOOD_AWAY_INTERCEPT + (median_income[0] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (median_income[1] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (median_income[2] * FOOD_AWAY_VAR_1),
                     FOOD_AWAY_INTERCEPT + (median_income[3] * FOOD_AWAY_VAR_1)]
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
        alcoholic_beverages = [ALCOHOL_INTERCEPT + (median_income[0] * ALCOHOL_VAR_1),
                               ALCOHOL_INTERCEPT + (median_income[1] * ALCOHOL_VAR_1),
                               ALCOHOL_INTERCEPT + (median_income[2] * ALCOHOL_VAR_1),
                               ALCOHOL_INTERCEPT + (median_income[3] * ALCOHOL_VAR_1)]
        df.loc[7] = ['2019 Alcoholic Beverages',
                     alcoholic_beverages[0] * households[0],
                     alcoholic_beverages[1] * households[1],
                     alcoholic_beverages[2] * households[2],
                     alcoholic_beverages[3] * households[3]]
        df.loc[8] = ['2019 Alcoholic Beverages (Household Average)',
                     alcoholic_beverages[0],
                     alcoholic_beverages[1],
                     alcoholic_beverages[2],
                     alcoholic_beverages[3]]
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
        beer_ale = [PCT_BEER * df.iat[8, 1],
                    PCT_BEER * df.iat[8, 2],
                    PCT_BEER * df.iat[8, 3],
                    PCT_BEER * df.iat[8, 4]]
        df.loc[11] = ['2019 Beer and Ale',
                      beer_ale[0] * households[0],
                      beer_ale[1] * households[1],
                      beer_ale[2] * households[2],
                      beer_ale[3] * households[3]]
        df.loc[12] = ['2019 Beer and ale (Household Average)',
                      beer_ale[0],
                      beer_ale[1],
                      beer_ale[2],
                      beer_ale[3]]
        wine = [PCT_WINE * df.iat[8, 1],
                PCT_WINE * df.iat[8, 2],
                PCT_WINE * df.iat[8, 3],
                PCT_WINE * df.iat[8, 4]]
        df.loc[13] = ['2019 Wine',
                      wine[0] * households[0],
                      wine[1] * households[1],
                      wine[2] * households[2],
                      wine[3] * households[3]]
        df.loc[14] = ['2019 Wine (Household Average)',
                      wine[0],
                      wine[1],
                      wine[2],
                      wine[3]]
        other_alcohol = [PCT_OTHER_ALCOHOL * df.iat[8, 1],
                         PCT_OTHER_ALCOHOL * df.iat[8, 2],
                         PCT_OTHER_ALCOHOL * df.iat[8, 3],
                         PCT_OTHER_ALCOHOL * df.iat[8, 4]]
        df.loc[15] = ['2019 Other Alcoholic Beverages',
                      other_alcohol[0] * households[0],
                      other_alcohol[1] * households[1],
                      other_alcohol[2] * households[2],
                      other_alcohol[3] * households[3]]
        df.loc[16] = ['2019 Other Alcoholic Beverages (Household Average)',
                      other_alcohol[0],
                      other_alcohol[1],
                      other_alcohol[2],
                      other_alcohol[3]]
        tobacco = [0, 0, 0, 0]
        for index, value in enumerate(median_income):
            tobacco[index] = TOBACCO_INTERCEPT + value * TOBACCO_VAR_1 + value ** 2 * TOBACCO_VAR_2
            tobacco[index] += value ** 3 * TOBACCO_VAR_3 + value ** 4 * TOBACCO_VAR_4
        df.loc[17] = ['2019 Tobacco products and smoking supplies',
                      tobacco[0] * households[0],
                      tobacco[1] * households[1],
                      tobacco[2] * households[2],
                      tobacco[3] * households[3]]
        df.loc[18] = ['2019 Tobacco products and smoking supplies (Household Average)',
                      tobacco[0],
                      tobacco[1],
                      tobacco[2],
                      tobacco[3]]
        cigarettes = [PCT_CIGARETTES * df.iat[18, 1],
                      PCT_CIGARETTES * df.iat[18, 2],
                      PCT_CIGARETTES * df.iat[18, 3],
                      PCT_CIGARETTES * df.iat[18, 4]]
        df.loc[19] = ['2019 Cigarettes',
                      cigarettes[0] * households[0],
                      cigarettes[1] * households[1],
                      cigarettes[2] * households[2],
                      cigarettes[3] * households[3]]
        df.loc[20] = ['2019 Cigarettes (Household Average)',
                      cigarettes[0],
                      cigarettes[1],
                      cigarettes[2],
                      cigarettes[3]]
        other_tobacco = [PCT_OTHER_TOBACCO * df.iat[18, 1],
                         PCT_OTHER_TOBACCO * df.iat[18, 2],
                         PCT_OTHER_TOBACCO * df.iat[18, 3],
                         PCT_OTHER_TOBACCO * df.iat[18, 4]]
        df.loc[21] = ['2019 Other Tobacco Products',
                      other_tobacco[0] * households[0],
                      other_tobacco[1] * households[1],
                      other_tobacco[2] * households[2],
                      other_tobacco[3] * households[3]]
        df.loc[22] = ['2019 Other Tobacco Products (Household Average)',
                      other_tobacco[0],
                      other_tobacco[1],
                      other_tobacco[2],
                      other_tobacco[3]]
        smoking_accessories = [PCT_ACCESSORIES * df.iat[18, 1],
                               PCT_ACCESSORIES * df.iat[18, 2],
                               PCT_ACCESSORIES * df.iat[18, 3],
                               PCT_ACCESSORIES * df.iat[18, 4]]
        df.loc[23] = ['2019 Smoking Accessories',
                      smoking_accessories[0] * households[0],
                      smoking_accessories[1] * households[1],
                      smoking_accessories[2] * households[2],
                      smoking_accessories[3] * households[3]]
        df.loc[24] = ['2019 Smoking Accessories (Household Average)',
                      smoking_accessories[0],
                      smoking_accessories[1],
                      smoking_accessories[2],
                      smoking_accessories[3]]

        return df

    def __get_sales_potential_expenditure(self):
        food_alcohol_expenditure = self.__get_food_alcohol_expenditure()
        automotive_expenditure = self.__get_automotive_expenditure()
        PCT_RESTAURANT = 0.473080402850928
        households = [self.combined_data['2020 HH'][0],
                      self.combined_data['2020 HH'][1],
                      self.combined_data['2020 HH'][2],
                      self.combined_data['2020 HH'][3]]
        df = pd.DataFrame({'DEMAND REPORT': [], '0.5-Mile Radius': [], '0.75-Mile Radius': [],
                           '1.0-Mile Radius': [], '1.25-Mile Radius': []})
        df.loc[0] = ['RETAIL SALES POTENTIAL', '', '', '', '']
        df.loc[1] = ['2020 Convenience Stores', '', '', '', '']
        df.loc[2] = ['2020 Gasoline Stations with Convenience Stores', '', '', '', '']
        df.loc[3] = ['2020 Beer, Wine, and Liquor Stores',
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[10, 1] * households[0],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[10, 2] * households[1],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[10, 3] * households[2],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[10, 4] * households[3]]
        df.loc[4] = ['2020 Supermarkets and Other Grocery (Except Convenience) Stores', '', '', '', '']
        df.loc[5] = ['2020 Restaurant Expenditures',
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[3, 1] * households[0],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[3, 2] * households[1],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[3, 3] * households[2],
                     PCT_RESTAURANT * food_alcohol_expenditure.iat[3, 4] * households[3]]
        df.loc[6] = ['', '', '', '', '']
        df.loc[7] = ['HOUSEHOLD EXPENDITURES', '', '', '', '']
        df = pd.concat([df, automotive_expenditure, food_alcohol_expenditure])

        return df


class TradeArea:
    def __init__(self, report):
        self.acs_data_current = report.acs_data_current
        self.combined_data = report.combined_data

    def get_trade_area(self):
        vehicle_1 = int(self.acs_data_current['Vehicles1'][1])
        vehicle_2 = 2 * int(self.acs_data_current['Vehicles2'][1])
        vehicles_GE3 = 3.2 * int(self.acs_data_current['VehiclesGE3'][1])
        df = pd.DataFrame({'Trade Area': [], '0.75 Mile': [], 'Value': []})
        df.loc[0] = ['2020 Population', '0.75-Mile',
                     self.combined_data['2020 Pop'][1]]
        df.loc[1] = ['2020 Households', '0.75-Mile',
                     self.combined_data['2020 HH'][1]]
        df.loc[2] = ['% Household Change 2020-2024', '0.75-Mile',
                     '']
        df.loc[3] = ['2019 Average HH Income', '0.75-Mile',
                     self.combined_data['2020 Mean Inc'][1]]
        df.loc[4] = ['2019 Median HH Income', '0.75-Mile',
                     self.combined_data['2020 Median Inc'][1]]
        df.loc[5] = ['Total Household Vehicles', '0.75-Mile',
                     vehicle_1 + vehicle_2 + vehicles_GE3]
        df.loc[6] = ['Total Employees', '0.75-Mile',
                     self.combined_data['2020 Employees'][1]]
        df.loc[7] = ['Total Daytime Population at Home', '0.75-Mile',
                     self.combined_data['2020 Daytime Pop'][1] - df.iat[6, 2]]
        df.loc[8] = ['Density Class', '0.75-Mile', 'Suburban']

        return df
