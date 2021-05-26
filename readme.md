# COVID World Data Information
This is a program to gather, index and display information about the world's COVID situation, by country. 
Final project of Stanford's 'Code In Place' 2021 course.

## How it works
This program gathers information from two main sources:

- John Hopkins University of Medicine's GitHub pages: https://coronavirus.jhu.edu/about/how-to-use-our-data
- Our World in Data's GitHub pages: https://ourworldindata.org/coronavirus

It iterates through the .csv files forming a nested dictionary:

{
    country_name : {
        date : [confirmed, deaths, recovered, active, total population, vaccinated]
    }
}

After the information has been gathered and indexed, the user can choose a country and a date range.

The program will default to the first and/or last date available if: 
a) No date range is provided 
b) The dates aren't properly formatted
c) The values can't be processed 
d) The dates provided are before 03-22-2020 or after current day.

The program will check until the end date provided minus 1 day, to avoid trying to read values that haven't been published or updated yet.

The program will display the total population of the country followed by the confirmed cases, deaths, recovered patients, active cases and vaccination records for that specific time frame. Each request will display the numbers at the initial date, the final date, the increase both in numbers and percentage from start to end, and the minimum / maximum / average numbers for the values during that time frame.