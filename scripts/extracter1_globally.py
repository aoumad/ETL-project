"""
This script will downloads the John Hopkins COVD-19
time series datasets and merges them into one csv file
"""

import csv
from datetime import datetime
import requests # import a third party library for making http requests

CSV_FILE = {
    "confirmed": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
    "deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
    "recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
}

def main():
    """" Prepares our data structure and parses the original CSV files. """

    # Start by generating a skeleton dict and getting all the available dates.
    data_dict, dates_dict = generate_list()

    # Now after we have our skeleton dictionary ready
    # We need now to iterate over our 3 urls
    for kind, url in CSV_FILE.items():
        with requests.get(url) as resp:

            # Pass the response text into a csv.DictReader object
            reader = csv.DictReader(resp.text.splitlines())

            # Iterate over each row of the CSV file
            for row in reader:

                # Iterate over our available dates
                for k, v in dates_dict.items():

                    # Construct the key for our look up
                    temp_key = "{}_{}".format(v, row["Country/Region"])

                    # Update the corresponding value depending on the CSV data kind
                    if kind == "confirmed":
                        data_dict[temp_key][0] += int(row[k])
                    elif kind == "deaths":
                        data_dict[temp_key][1] += int(row[k])
                    elif kind == "recovered":
                        data_dict[temp_key][2] += int(row[k])
        # Save our data to a CSV file
        with open("global_data.csv", "w", encoding="utf-8", newline="") as other_file:

            # Initialize the data list with the header row
            data_list = [
                ["isodate", "country", "confirmed", "deaths", "recovered"]
            ]

            # Iterate over our data dict and pass the values to the data list
            for k, v in data_dict.items():
                isodate, country = k.split("_")
                data_list.append([isodate, country, v[0], v[1], v[2]])

            csv.writer(other_file).writerows(data_list)


def generate_list():
    """" Prepares a list with all the available countries and all the available dates
    This list will contains dummy values that will be later filled.

    Returns
    -------
    """

    # Create a new empty dictionary that will be used as a skeleton for storing data
    data_dict = dict() # dict is a built-in python function that creates a new dictionary

    # THis dictionary will hold all our available dates
    dates_dict = dict()

    # This set will hold all the countries/regions we found
    countries = set() # built-in function in python used to create an empty set (when used with no argument) + it's implemented using a hash table

    # We will load the first CSV url
    file = list(CSV_FILE.values())[0]

    # with requests.get(file, timeout=0) as resp:
    with requests.get(file) as resp:

        # Pass the response text into a csv.DictReader object
        reader = csv.DictReader(resp.text.splitlines())

        #Extract the header row and select from the fifth column onwards
        fields = reader.fieldnames[4:]

        # Convert the header row dates to datetime objects
        for field in fields:
            dates_dict[field] = "{:%Y-%m-%d}".format(
                datetime.strptime(field, "%m/%d/%y")
            )

        # Extract the countries/regions by iterating over all rows
        for row in reader:
            countries.add(row["Country/Region"])

        # Convert the countries set to a list and sort it
        countries = sorted(list(countries))

        # Combine every date with every country and fill it with zero values
        for date in dates_dict.values():
            for country in countries:
                temp_key = "{}_{}".format(date, country) # it will make see an output like this '2020-01-22_Afghanistan'
                data_dict[temp_key] = [0, 0, 0]

    return data_dict, dates_dict

if __name__ == "__main__":
    main()