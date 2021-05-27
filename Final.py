import csv
import requests
from datetime import date, timedelta


COUNTRY_POPULATION = 'https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/world_pop_by_country.csv'
COUNTRY_VACCINATIONS = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
COUNTRY_DEATHS_CASES = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'


def main():
    """ Data pre-loading state. """
    print("Please wait, collecting all available data...")
    final_data = collect_data()
    print("Ready!")
    """ Pre-loading done"""

    """ Get user input to process and display the stored information """
    data_management(final_data)


# Function to display the gathered information based on user choice of country and date range.
def data_management(data):
    user_country = choose_country()
    while user_country != "":
        if user_country in data:
            while True:
                user_range = get_user_date_range()  # obtain list with range of dates to perform the search

                """ Information display """
                print("\n>>> " + user_country + ", available data between " + user_range[0] + " and " + user_range[-1] + ":")

                # Total population
                total_pop = data[user_country][user_range[0]][4]
                print("\n\t# Total population:", total_pop)

                # Confirmed cases
                print("\n\t# Confirmed cases:")
                print_values(data, user_country, user_range, 0, total_pop)

                # Deaths
                print("\n\t# Deaths:")
                print_values(data, user_country, user_range, 1, total_pop)

                # Recovered
                print("\n\t# Recovered:")
                print_values(data, user_country, user_range, 2, total_pop)

                # Active cases
                print("\n\t# Active cases:")
                print_values(data, user_country, user_range, 3, total_pop)

                # Vaccinations
                print("\n\t# Vaccinations:")
                print_values(data, user_country, user_range, 5, total_pop)

                # Check at the end if user wants to perform another search in same country, or exit to country selection
                choice = input("\nWould you like to check another range of dates in this same country? (Y/N): ").lower()
                if choice != "y":
                    break

        elif user_country == "LIST":
            print("\nHere is a list of available countries / zones:")
            # Create an empty list for the values
            country_list = []
            # Add keys (country names) to the list
            for country in data.keys():
                country_list.append(country)
            # Sort them alphabetically
            country_list.sort()
            # Print sorted values
            for country in country_list:
                print("- " + country)
            print()  # blank space for readability

        else:
            print("Sorry, I don't have any information about the country or zone " + user_country + ".")
            # Try to retrieve countries that start with the value the user introduced
            similar = obtain_similar(data, user_country)
            if len(similar) > 0:
                print("Maybe you meant one of these instead?:")
                for c in similar:
                    print("- " + c)

        user_country = choose_country()
    print("Goodbye!")


# Function to retrieve a list of countries that start with the input the user entered
def obtain_similar(data, user_country):
    # Create empty list to save possible similar countries
    similar_list = []
    # Iterate conuntries and add to the list the ones that start with the value that user introduced
    for country in data.keys():
        if country.startswith(user_country):
            similar_list.append(country)
    return similar_list


# Function to ask for a country and return a full uppercase value without side spaces
def choose_country():
    # Ask user to choose a country, quit or display a list
    user_country = input("\nWhat country do you want to get information about?\nType a country name, LIST for a list of available countries, or press enter to exit: ")

    # If user presses enter, return immediately
    if user_country == "":
        return ""

    return user_country.strip().upper()


# Function to print all the values of a given position in the list of values
def print_values(data, user_country, user_range, position_in_list, total_pop):
    # Store minimum, maximum, average and difference in values
    min_max_avg_diff = calculate_min_max_avg_diff(data, user_country, user_range, position_in_list)
    # Store start and end values of the time frame
    start_value = data[user_country][user_range[0]][position_in_list]
    end_value = data[user_country][user_range[-1]][position_in_list]

    # Initial value
    print("\t\tAt initial date:", start_value, end="")
    percentage_of_total = calculate_percentage(total_pop, start_value)
    print(" (" + str(percentage_of_total) + "% of the country's total population)")

    # Final value
    print("\t\tAt final date:", end_value, end="")
    percentage_of_total = calculate_percentage(total_pop, end_value)
    print(" (" + str(percentage_of_total) + "% of the country's total population)")

    # Calculate percentage of increase or decrease and then print the difference between start and end date.
    percentage_of_total = calculate_increase_decrease(start_value, end_value)
    if percentage_of_total >= 0:
        print("\t\t(+) Increased in this lapse of time by:", min_max_avg_diff[3], end="")
        print(" (" + str(percentage_of_total) + "% increase)")
    else:
        print("\t\t(-) Decreased in this lapse of time by:", min_max_avg_diff[3], end="")
        print(" (" + str(percentage_of_total) + "% decrease)")

    # Values only displayed in case of a fluctuating number (Active cases)
    if position_in_list == 3:
        # Minimum
        print("\t\tMinimum:", min_max_avg_diff[0], end="")
        percentage_of_total = calculate_percentage(total_pop, min_max_avg_diff[0])
        print(" (" + str(percentage_of_total) + "% of the country's total population)")

        # Maximum
        print("\t\tMaximum:", min_max_avg_diff[1], end="")
        percentage_of_total = calculate_percentage(total_pop, min_max_avg_diff[1])
        print(" (" + str(percentage_of_total) + "% of the country's total population)")

    # Average
    print("\t\tAverage:", min_max_avg_diff[2], end="")
    percentage_of_total = calculate_percentage(total_pop, min_max_avg_diff[2])
    print(" (" + str(percentage_of_total) + "% of the country's total population)")


# Function to calculate the percentage of increase or decrease in number
def calculate_increase_decrease(start_value, end_value):
    # If initial result is zero, it isn't possible to calculate
    if start_value == 0:
        return 0
    return round(end_value * 100 / start_value - 100, 2)


# Function to return the percentage number of the total population
def calculate_percentage(total_pop, average):
    # In case there is any error retrieving total population, avoid division by zero by returning 0
    if total_pop == 0:
        return 0
    return round(average * 100 / total_pop, 2)


# Function to calculate the minimum, maximum, average values and the difference between initial and final values.
def calculate_min_max_avg_diff(data, user_country, user_range, position_in_list):
    # Initialize amount of dates checked and the total numbers
    total_dates = 0
    total_amount = 0
    # Initialize minimum and max values found to first date in list
    minimum_value = data[user_country][user_range[0]][position_in_list]
    maximum_value = data[user_country][user_range[0]][position_in_list]
    # Difference in number between end and start date
    diff = data[user_country][user_range[-1]][position_in_list] - data[user_country][user_range[0]][position_in_list]

    for specific_date in user_range:
        current_number = data[user_country][specific_date][position_in_list]  # current checked number
        total_amount += current_number
        total_dates += 1
        if current_number < minimum_value:
            minimum_value = current_number
        elif current_number > maximum_value:
            maximum_value = current_number

    return [minimum_value, maximum_value, total_amount // total_dates, diff]


# Obtain list with all possible dates between 2020-03-22 and today.
def get_full_date_range():
    # Get start and end date in YYYY-MM-DD format
    sdate = date(2020, 3, 22)  # start date
    edate = date.today()  # end date

    delta = edate - sdate  # as timedelta

    # List with all dates:
    date_list = []

    # Iterate through range of days, converting it to GitHub format, and adding it to the list
    for i in range(delta.days):
        day = sdate + timedelta(days=i)
        day = convert_github_format(day)
        date_list.append(day)
    return date_list


# Function to obtain and validate date range provided by user
def get_user_date_range():
    print("I need a start and end date between 03-22-2020 and today in MM-DD-YYYY format, leave blank for full range.")

    start = input("Start date: ").split("-")
    end = input("End date: ").split("-")

    try:
        sdate = date(int(start[2]), int(start[0]), int(start[1]))  # start date
    except (ValueError, IndexError):
        sdate = date(2020, 3, 22)  # revert to default if there is any error

    try:
        edate = date(int(end[2]), int(end[0]), int(end[1]))  # end date
    except (ValueError, IndexError):
        edate = date.today()  # revert to default if there is any error

    # If user writes a later date on the start than the end, swap the numbers
    if sdate > edate:
        temp = sdate
        sdate = edate
        edate = temp

    # If user writes values similar to a date but out of the scope, default that value to the lowest / highest available date
    if sdate < date(2020, 3, 22):
        sdate = date(2020, 3, 22)
    elif sdate > date.today():
        sdate = date.today()

    if edate > date.today():
        edate = date.today()
    elif edate < date(2020, 3, 22):
        edate = date(2020, 3, 22)

    # If user writes same value on start and end date, get one day earlier or later without going out of bounds
    if sdate == edate:
        if edate < date.today() - timedelta(days=1):
            edate = edate + timedelta(days=1)
        elif sdate > date(2020, 3, 22):
            sdate = sdate - timedelta(days=1)

    delta = edate - sdate  # as timedelta

    # List with dates chosen by user:
    date_list = []

    # Iterate through range of days, converting it to GitHub format, and adding it to the list
    for i in range(delta.days):
        day = sdate + timedelta(days=i)
        day = convert_github_format(day)
        date_list.append(day)
    return date_list


# Function to convert date to John Hopkins' GitHub format in the csv files
def convert_github_format(chosen_date):
    day = str(chosen_date.day)
    month = str(chosen_date.month)
    year = str(chosen_date.year)

    if chosen_date.day // 10 == 0:
        day = "0" + str(chosen_date.day)
    if chosen_date.month // 10 == 0:
        month = "0" + str(chosen_date.month)

    return month + "-" + day + "-" + year


# Function to collect all the different data from every resource
def collect_data():
    """
    Create empty dictionary to be progressively filled up like:
        {
            country_name : {
                date : [confirmed, deaths, recovered, active, total population, vaccinated]
            }
        }
    """
    final_data = {}
    date_range = get_full_date_range()  # obtain date range between 03-22-2020 (initial consistent data) and today
    compute_information(final_data, date_range)  # obtain dictionary filled with everything except vaccinations and total pop

    # Add total population to our dictionary
    final_data = collect_countries_pop(final_data)

    # Add vaccinated information to the values
    final_data = collect_countries_vaccinated(final_data)

    return final_data


# Function to compute all information of all different dates and pack it in a structured dictionary
def compute_information(final_data, date_range):
    print("Pre-loading information about deaths and confirmed / recovered / active cases for the full available date range...")
    print("(This may take a while, please stand by)... ", end="")
    for day in date_range:
        # Use the web adress with the start of the link + current day in the iteration + .csv at the end for the full link
        web_info = requests.get(COUNTRY_DEATHS_CASES + day + ".csv").text.splitlines()
        reader = csv.reader(web_info)
        # Jump first line (headers)
        next(reader)
        for row in reader:
            # Try to cast values to int, leaving empty strings at value 0
            confirmed = 0
            deaths = 0
            recovered = 0
            active = 0
            try:
                confirmed = int(row[7])
                deaths = int(row[8])
                recovered = int(row[9])
                active = int(row[10])
            except ValueError:
                pass

            # If value is not in countries dictionary (protection against repeated country names), add it
            country = row[3].upper()  # convert country to all uppercase to make searching easier
            if country not in final_data:
                inside_dictionary = {day: [confirmed, deaths, recovered, active]}
                final_data[country] = inside_dictionary
            else:
                # If we don't have any values already written for that country in that given day
                if day not in final_data[country]:
                    final_data[country][day] = [confirmed, deaths, recovered, active]
                # If we have already written values for than country in that given day, we have multiple inputs for same country, so we add them up
                else:
                    # Overwrite each value in the values list on each date adding up the corresponding value in the current row
                    final_data[country][day][0] += confirmed
                    final_data[country][day][1] += deaths
                    final_data[country][day][2] += recovered
                    final_data[country][day][3] += active
    print("Done.")
    return final_data


# Function to add countries and population to our retrieved data
def collect_countries_pop(data):
    print("Pre-loading latest world population data... ", end="")
    web_info = requests.get(COUNTRY_POPULATION).text.splitlines()
    reader = csv.reader(web_info)
    # Jump first line (headers)
    next(reader)

    for row in reader:
        country = row[0].upper()
        # If the country exists in the dictionary
        if country in data:
            # At every specific date inside the country, append the world pop at the last position
            for specific_date in data[country]:
                try:
                    data[country][specific_date].append(int(row[2]))
                # If there is any error in the values (or empty) set value to 0
                except ValueError:
                    data[country][specific_date].append(0)

    # Do one last iteration to set to 0 the population values and vaccinated values of the countries not in the population csv
    for country in data:
        for specific_date in data[country]:
            # If we are missing population data or any other parameter,
            # fill values with zeroes until we have a list of 5 elements to work with them later
            while len(data[country][specific_date]) < 6:
                data[country][specific_date].append(0)

    print("Done.")
    return data


# Function to add number of vaccinations to our retrieved data
def collect_countries_vaccinated(data):
    print("Pre-loading latest vaccination data... ", end="")
    web_info = requests.get(COUNTRY_VACCINATIONS).text.splitlines()
    reader = csv.reader(web_info)
    # Jump first line (headers)
    next(reader)

    for row in reader:
        country = row[0].upper()
        # Change country to US because JHUM's data indexes it that way
        if country == "United States":
            country = "US"
        # If the country is in the dictionary
        if country in data:
            # Convert date to MM-DD-YYYY and if the date is present inside the country
            formatted_date = format_mm_dd_yyyy(row[2])
            if formatted_date in data[country]:
                try:
                    total_vaccinations = int(row[3])
                except ValueError:
                    total_vaccinations = 0
                # Add the vaccinated people at that country and date replacing the last position in the list (vaccinations)
                data[country][formatted_date][-1] = total_vaccinations

    # Now we must normalize the vaccination data, because we will have zeroes between specific recount dates
    for country in data:
        # Save the minimum value we have received so far in the vaccinations. Will reset for each country
        vaccine_recount_to_date = 0
        # Values are iterated from past to present
        for specific_date in data[country]:
            # If the value is lower than the lowest value we have, we overwrite that position with the lowest
            if data[country][specific_date][-1] < vaccine_recount_to_date:
                data[country][specific_date][-1] = vaccine_recount_to_date
            # If the value is higher than the lowest value we have, we overwrite the highest with that value
            elif data[country][specific_date][-1] > vaccine_recount_to_date:
                vaccine_recount_to_date = data[country][specific_date][-1]
    print("Done.")
    return data


# Function to convert YYYY-MM-DD date format to MM-DD-YYYY
def format_mm_dd_yyyy(yyyy_mm_dd):
    return yyyy_mm_dd[5:7] + "-" + yyyy_mm_dd[8:] + "-" + yyyy_mm_dd[:4]


if __name__ == '__main__':
    main()
