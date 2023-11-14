import pandas as pd
import json

# %% load json data to a dataframe
with open('data/cars.json') as file:
    dat = json.load(file)

cars = pd.json_normalize(dat)

cars['make'] = cars['make'].astype('category')

cars['start_year'] = cars['model_years'].apply(lambda years: int(years[:4])) # take the first half of 'model_years' as the start year
cars['end_year'] = cars['model_years'].apply(lambda years: int(years[5:])) # take the second half of 'model_years' as end year. could set to datetype, but int is easier to plot

# %% create another dataframe that records the number of makes active each year 
years = [i for i in range(1900, 2025)]
df = pd.DataFrame({'year' : years, 'makes' : [set() for i in range(len(years))], 'count_makes': [[0] for i in range(len(years))]}) #dataframe columns: year, set of makes, count of makes

# for each year in df, see if each model was produced in the year. If it was, add the make of the car to the 'makes' set
for year_index, year_row in df.iterrows():
    for car_index, car_row in cars.iterrows():
        if year_row['year'] >= car_row['start_year'] and year_row['year'] <= car_row['end_year']:
            year_row['makes'].add(car_row['make'])

# for each year, find the count of 'makes'
for year_index, year_row in df.iterrows():
    year_row['count_makes'][0] = len(year_row['makes'])
        
# convert the count of 'makes' to an int. was a list before to make it mutable    
df['count_makes'] = df['count_makes'].apply(lambda makes: makes[0])    


# %% plot

x_ticks = [i for i in range(1900, 2025, 15)]
y_ticks = [i for i in range(2, 21, 2)]

plot = df.plot(x = 'year', xticks = x_ticks, yticks = y_ticks, xlabel = 'Year', ylabel = 'Number of active makes', title = 'Makes of Cars Produced in the US')


# %%
# old implementation: take each model_years variable and turn it into an index of all the years the car was/is in production
#cars['model_years'] = cars['model_years'].apply(lambda years: pd.date_range(start = years[:4], end = years[5:], periods = (int(years[5:]) - int(years[:4]) + 1),inclusive='both').strftime('%Y'))
#date_ranges = cars['model_years'].apply(lambda years: pd.date_range(start = years[:4], end = years[5:], periods = (int(years[5:]) - int(years[:4]) + 1),inclusive='both').strftime('%Y'))
