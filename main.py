import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from iso3166 import countries
from datetime import datetime

# Options for terminal -----------------------------------------------
pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# --------------------------------------------------------------------

df_data = pd.read_csv("data/mission_launches.csv")
old_shape = df_data.shape

print("-----------Data details before clearing and adding new columns------\n")
print("Shape of data is: \n", old_shape, "\n")
print(f"It has: {old_shape[0]} rows.\n And {old_shape[1]} columns.\n")
print("Names of the columns: \n", df_data.columns.values.tolist(), "\n")
print("Nan values: \n", df_data.isna().sum(), "\n")
print("Duplicates: \n", df_data.duplicated().value_counts())

print("------------------------cleared data-------------------------\n")
# Delete two columns that are just duplicated index
cleared_data = df_data
del cleared_data['Unnamed: 0.1']
del cleared_data['Unnamed: 0']

print(f"Cleared data: \n {cleared_data.head(3)}")

print("---------------------------New state, country_code columns----------------------------\n")
whole_loc = [row.split(",") for row in cleared_data["Location"]]
states = [name for name in whole_loc]

# -----------For changing locations to normal state names---------------------
new_states = []
for row in states:

    for state in row:
        if state in [" Kazakhstan", " Russia", " Barents Sea"]:
            state = "Russian Federation"
            new_states.append(state)
            break
        elif state in [" USA", " New Mexico", " Pacific Missile Range Facility", " Gran Canaria", ' Pacific Ocean']:
            state = "USA"
            new_states.append(state)
            break
        elif state in [" China", " Yellow Sea"]:
            state = "China"
            new_states.append(state)
            break
        elif state == " Japan":
            state = "Japan"
            new_states.append(state)
            break
        elif " New Zealand" == state:
            state = "New Zealand"
            new_states.append(state)
            break
        elif state == " India":
            state = "India"
            new_states.append(state)
            break
        elif state == " France":
            state = "France"
            new_states.append(state)
            break
        elif state in [" Shahrud Missile Test Site", " Iran"]:
            state = "Iran, Islamic Republic of"
            new_states.append(state)
        elif state == " Israel":
            state = "Israel"
            new_states.append(state)
            break
        elif state == " North Korea":
            state = "Korea, Democratic People's Republic of"
            new_states.append(state)
            break
        elif state == " South Korea":
            state = "Korea, Republic of"
            new_states.append(state)
            break
        elif state == " Australia":
            state = "Australia"
            new_states.append(state)
            break
        elif state == " Brazil":
            state = "Brazil"
            new_states.append(state)
            break
        elif state == " Kenya":
            state = "Kenya"
            new_states.append(state)
            break

# For control which states I missed.
# unique_states = []
# for row in states:
#     if row[-1] not in unique_states:
#         unique_states.append(row[-1])
#     else:
#         continue

cleared_data["States"] = new_states

# ---------------------Create country codes and append to Data Frame-----------

# Some states have really complicated ISO3166 names. For control if name is working
# print(countries.get("Korea, Democratic People's Republic of"))

country_codes = []
for country in new_states:
    code = countries.get(country)
    country_codes.append(code[2])

cleared_data["Country_Codes"] = country_codes

columns_to_print = ["States", "Country_Codes"]
print(f"New columns added to DataFrame: \n{cleared_data[columns_to_print].head(5)}\n")

print("-----------------------NAN values----------------------------\n")
missing = np.where(cleared_data.Price.isnull() == True)
print(f"Missing values in column Price:\n{len(missing[0])}")

# I can't use .dropna() function because a lot of values would be lost.
# cleared_data = cleared_data.dropna()

print("-----------Filling Nan values with median by name of organisation----------")
print(f"Number Nan values in Price: \n{cleared_data['Price'].isna().sum()}")
# ----------Changing str to float and add price to nan values---------------------------
str_price = cleared_data["Price"]
float_price = []

for num in str_price:
    try:
        price = float(num.replace(",", ""))
        float_price.append(price)
    except AttributeError:
        price = 16.5               # Average price per states. It is better than lost around 3000 entries in DataFrame
        float_price.append(price)

# Changing str to float
cleared_data["Price"] = float_price

# Add median value by state to nan values
median_prices = cleared_data.groupby("States")["Price"].mean()

print("Distribution of prices")
histogram = cleared_data.hist(column="Price",       # Column to plot
                              figsize=(9, 6),       # Plot size
                              bins=54               # Number of histogram bins
                              )
plt.show()

# -------------Create two columns from Detail: Rocket_Name and Payload--------------
whole_rocket_name = [row.split("|") for row in cleared_data["Detail"]]
rocket_name = [name[0] for name in whole_rocket_name]
payload = [name[1] for name in whole_rocket_name]

# Add new columns Rocket_Name and Payload
cleared_data["Rocket_Name"] = rocket_name
cleared_data["Payload"] = payload

payload_rocket = ["Payload", "Rocket_Name"]
print(f"New columns Payload and Rocket name:\n {cleared_data[payload_rocket].head(5)}\n")

# -------------Deleting old column Detail--------------------------------------------
del cleared_data["Detail"]

# Meanings of the column names:
# Organisation:   Name of organisation
# Location:       Place where was launch executed
# Date:           Date of rocket start
# Detail:         What was that rocket and payload
# Rocket_status:  If rocket is still in use.
# Mission_status: Success or failure of mission.
# States:         Name of state
# Country_Codes:  Codes of specific country
# Rocket_Name:    Name of the rocket
# Payload:        Name of the payload

print("-----------------DataFrame details after cleaning + new columns------------------------------\n")
data_shape = cleared_data.shape
print("Shape of data is: \n", data_shape)
print(f"It has: {data_shape[0]} rows.\n And {data_shape[1]} columns.")
print("Names of the columns: \n", cleared_data.columns.values.tolist())
print("Nan values: \n", cleared_data.isna().count())
# print("Duplicates: \n", cleared_data.duplicated())

print("-----------Number of launches per company------------------\n")
launches = cleared_data["Organisation"].value_counts()
print(f"Number of launches per organisation: \n{launches}\n")

print("---------------------Number of Active versus Retired Rockets------------------------------\n")
# Active rockets
boolean_index_t = cleared_data["Rocket_Status"] == "StatusActive"

# Retired Rockets
boolean_index_f = cleared_data["Rocket_Status"] != "StatusActive"

# Using boolean index to get active and decommissioned rockets
active = cleared_data.loc[boolean_index_t, "Rocket_Name"].nunique()
inactive = cleared_data.loc[boolean_index_f, "Rocket_Name"].nunique()

print(f'Number of still active rockets is: {active}. \n'
      f'Number of retired rockets is: {inactive}.\n')

print("-------------Number of successful missions vs. failed-----------------------")

success_bool = cleared_data["Mission_Status"] == "Success"
failed_bool = cleared_data["Mission_Status"] != "Success"

success = cleared_data.loc[success_bool, "Organisation"].value_counts()
failed = cleared_data.loc[failed_bool, "Organisation"]. value_counts()

# Creating Mission_Status_Int as column with values as integers
mission_int = []
for num in cleared_data["Mission_Status"]:
    if num == "Success":
        mission_int.append(2)
    else:
        mission_int.append(1)

cleared_data["Mission_Status_Int"] = mission_int
print(f'Mission status as int: \n{cleared_data["Mission_Status_Int"].head(20)}')
# -----------------------------------------------------------------------------------

print(f"Number of successes vs failed missions by Organisation: \n{success} \nFailed missions:\n {failed}.\n")

print("------------------Price per launch-----------------")
print(f"Number Nan values in Price: \n{cleared_data['Price'].isna().sum()}")

# ------------------Histogram average Price per launch by organisation-----------------
grouped_df = cleared_data.groupby("Organisation")["Price"].mean().reset_index()

plt.bar(grouped_df["Organisation"], grouped_df["Price"])
plt.xlabel('Organisation')
plt.xticks(rotation=45, ha="right")
plt.ylabel("Price per launch")
plt.title("Histogram of average prices per launches by organisations")
plt.show()
# ------------------------------Launches per state map --------------------------------------------------------
locations = cleared_data["Country_Codes"].unique()

set_states_values = cleared_data["States"].value_counts()

state_names = cleared_data["States"].unique()

print("----------------------Map of launches per country-----------------")
launches_per_state = go.Figure(data=go.Choropleth(
                                   locations=locations,
                                   z=set_states_values,
                                   text=state_names,
                                   colorscale="Blues",
                                   autocolorscale=True,
                                   reversescale=False,
                                   )
                               )

launches_per_state.update_layout(title_text="Launches per State",
                                 geo=dict(showframe=True,
                                          showcoastlines=True,
                                          projection_type='equirectangular'),
                                 annotations=[dict(x=0.55,
                                                   y=0.1,
                                                   xref="paper",
                                                   yref='paper',
                                                   text='Source: <a href="https://colab.research.google.com/drive/'
                                                        '1YpZRVy16KqLuKvqJifzukBT2TQMj8VX1#scrollTo=xdolY0-Sa-p1">'
                                                        'Space_Missions_Analysis</a>',
                                                   showarrow=True
                                                   )]
                                 )
launches_per_state.show()

# ----------------------Failure per state map----------------------------
fails_per_state = go.Figure(data=go.Choropleth(
                                                locations=locations,
                                                z=failed,
                                                colorscale="Reds",
                                                autocolorscale=True,
                                                reversescale=True
                                                )
                            )

fails_per_state.update_layout(
                                 title_text="Fails per state",
                                 geo=dict(
                                          showframe=True,
                                          showcoastlines=True,
                                          projection_type='equirectangular'
                                          ),
                                 annotations=[dict(x=0.55,
                                                   y=0.1,
                                                   xref="paper",
                                                   yref='paper',
                                                   text='Source: <a href="https://colab.research.google.com/drive/'
                                                        '1YpZRVy16KqLuKvqJifzukBT2TQMj8VX1#scrollTo=xdolY0-Sa-p1">'
                                                        'Space_Missions_Analysis</a>',
                                                   showarrow=True
                                                   )]
                                 )
fails_per_state.show()

# -------SunBurst chart of the countries, organisations, and mission status--------
print("-----------------SunBurst-Launches per state and company, Successes/failures--------------------\n")

sunburst_graph = px.sunburst(cleared_data,
                             path=["States", "Organisation", "Mission_Status"],
                             values="Mission_Status_Int",
                             branchvalues="total",
                             )

sunburst_graph.update_layout(title="Launches per state and company, Successes/failures")
sunburst_graph.show()

# ----------Money spend by organisations on space missions-------------.
price_per_comp = cleared_data.groupby("Organisation")['Price'].sum()

figure = px.sunburst(cleared_data,
                     path=[cleared_data["Organisation"].unique()],
                     values=price_per_comp,
                     branchvalues="total",)
figure.update_layout(title="Money spend by organisation on space missions")
figure.show()
# ---------------------Number of launches per year-----------------------------

# ----------Convert string to datetime object--------
# stripping unnecessary parts of string

new_date = []
for row in cleared_data["Date"]:
    date_list = row.split()
    if len(date_list) > 4:
        date_str = f"{date_list[0]} {date_list[1]} {date_list[2]} {date_list[3]}"
        new_date.append(date_str)
    else:
        new_date.append(row)

# Adding new Stripped strings to column Date
cleared_data["Date"] = new_date

# print(cleared_data["Date"].head(5), "\n", cleared_data["Date"].tail(5))

# Converting str to datetime object
date = []
for row in cleared_data["Date"]:
    try:
        new_date = datetime.strptime(row, "%a %b %d, %Y")
        date.append(new_date)
    except ValueError:
        print(row)

# Appending new data to column Date
cleared_data["Date"] = date
print(type(cleared_data["Date"][0]))

print("Grouping data by organisation and date of launch:\n")
filter_date = ['Organisation', "Date"]
filtered_data = cleared_data[filter_date]

# Create new column just with years
cleared_data["Year"] = filtered_data['Date'].dt.year
print(cleared_data[["States", "Year"]].head(10))

# ---------------------------Launches over years---------------------------------
launches_dates = px.line(cleared_data,
                         x="Year",
                         color="States",
                         markers=True,
                         title="Number of launches per Organisation over years",
                         labels={"Year": 'Year', 'States': "State",
                                 "Date": 'Number of Launches'})
launches_dates.show()

# ----------------Number of launches per month-------------------

cleared_data["Month"] = filtered_data["Date"].dt.month

monthly_launches = px.line(cleared_data,
                           x="Month",
                           color="States",
                           markers=True,
                           title="Number of launches per state over months",
                           labels={"Month": 'Month',
                                   "States": "State",
                                   "Date": "Number of Launches"})
monthly_launches.show()

# The most popular months are : Jun, July, August
# Least popular are winter months: December, January, February

# ---------------Launch price over time-------------
price_per_date = cleared_data[["Date", "Price"]]

launches_over_time = px.line(price_per_date,
                             x="Date",
                             color="Price",
                             markers=False,
                             title="Price per Launch over time",
                             )
launches_over_time.show()

# Problem with this chart is: a Lot of price data was Nan. I supplied it with: Average price in missing years
# Not missing values suggest that price per launch over years are descending.

# -----------------Number of launches over tyme by top 10 organisations-----------------
print("-----------------Number of launches over tyme by top 10 organisations-----------------\n")

# Select top 10 organisation
top_10_org = cleared_data["Organisation"].value_counts().head(10)
org_names = top_10_org.index.tolist()

# Filter cleared_data by org_names
filtered_data = cleared_data[cleared_data['Organisation'].isin(org_names)]

plt.bar(filtered_data["Organisation"], filtered_data["Date"])
plt.xlabel('Organisation')
plt.xticks(rotation=45, ha="right")
plt.ylabel("Dates of launches")
plt.title("Histogram number of launches per date")
plt.show()


print("------------------------Cold war USSR vs USA----------------------------")

# Filter params
filter_state = ["USA", "Russian Federation"]
filter_date = range(0, 1992)

# Filter data by name of State
ussr_usa = cleared_data[cleared_data["States"].isin(filter_state)]

# Filter data by year up to 1991
cold_war = ussr_usa[ussr_usa["Year"].isin(filter_date)]

# Plotly pie chart total number of launches of the USSR and USA
cold_war_chart = px.pie(cold_war,
                        names="States",
                        values="Year",
                        color="States",
                        hole=0.3,
                        title="Number of launches per state over years",
                        labels={"names": 'States',
                                "values": "Number of launches"
                                })

cold_war_chart.show()

# ---------Create a Chart that Shows the Total Number of Launches Year-On-Year by the Two Superpowers-----

cold_war_chart = px.bar(cold_war,
                        x="Date",
                        color="States",
                        title="Total number of launches year-on-year by the USA and USSR")
cold_war_chart.show()

# -------------------Chart the total number of mission Failures-----------------------
figure = px.sunburst(cold_war,
                     path=[cold_war["States"], cold_war["Mission_Status"]],
                     branchvalues="total",)
figure.update_layout(title="Mission successes and failures by USSR and USA")
figure.show()

# ------------Chart the Total Number of Mission Failures Year on Year-----------

mission_stat_chart = px.bar(cleared_data,
                            x="Date",
                            color="Mission_Status_Int",
                            title="Total number of failures and successes by date")
mission_stat_chart.show()

# ----------------Chart the Percentage of Failures over Time---------------------
print("-------------Failures over time-----------------")

years_failures = cleared_data[["Year", "Mission_Status"]]
years_failures["Mission_Status"] = years_failures["Mission_Status"].apply(lambda x: 1
                                                                          if x == "Success" else 0)

percentage = years_failures.groupby('Year')['Mission_Status'].mean().reset_index()
percentage["Failure"] = 1 - percentage["Mission_Status"]

failure_chart = px.bar(percentage,
                       x="Year",
                       y=['Mission_Status', 'Failure'],
                       labels={'value': 'Percentage', 'variable': 'Mission Status'},
                       color_discrete_map={"Mission_Status": 'green', 'Failure': 'red'},
                       barmode='stack',
                       title="Percentage of successes over years"
                       )

failure_chart.show()

print("---------------Number of launches per year by countries----------------")

yearly_launches_country = cleared_data[["States", "Year"]]
grouped_number_of_launches = yearly_launches_country.groupby(["Year", "States"])
grouped_number_of_launches = grouped_number_of_launches.size().reset_index(name="Launches")

yearly_launches = px.line(grouped_number_of_launches,
                          x="Year",
                          y="Launches",
                          color="States",
                          markers=True,
                          title="Number of launches per state over Years",
                          labels={"Launches": 'Number of Launches',
                                  "Year": "Year"})
yearly_launches.show()

print("---------------Number of launches per year by organisations----------------")
yearly_launches_org = cleared_data[["Organisation", "Year"]]
grouped_org = yearly_launches_org.groupby(["Year", "Organisation"])
grouped_org = grouped_org.size().reset_index(name="Launches")

org_yearly_launches = px.line(grouped_org,
                              x="Year",
                              y="Launches",
                              color="Organisation",
                              markers=True,
                              labels={"Launches": "Number of Launches",
                                      "Year": "Year"},
                              title="Number of launches per organisation over years")
org_yearly_launches.show()
