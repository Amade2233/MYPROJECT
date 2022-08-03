from utils import *


URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

df = get_data(URL, get_sunday_date)
df_day = prepare_data_day(df).to_frame()

forecast = make_forecast(df_day)
prev_50 = get_last_n_days_data(df_day, forecast=forecast)

st.title("Technological University of the Shannon: Midlands Midwest")

bar = st.sidebar
option = bar.selectbox(
    "Select an option", ("7-day death cases forecast", "death cases in West Africa"), 0
)

if option == "7-day death cases forecast":
    sunday = get_sunday_date()
    next_sunday = (dt.fromisoformat(sunday) + timedelta(days=7)).isoformat()[:10]
    st.write("## A week forecast of death cases in West Africa")
    st.write(f"__from {sunday} to {next_sunday}__")
    st.write("__updated every sunday__")

    plot_forecast(prev_50)
    st.write("you can zoom in on chart; double click to reset chart")
    st.write(f"### Total deaths forecast for the week is {forecast.sum()}")

if option == "death cases in West Africa":
    st.write(f"## Covid-19 death trend in West Africa by country")
    st.write("__updated every sunday__")
    countries = st.multiselect(
        "Choose countries", ["All"] + list(df.index), ["Nigeria", "Ghana"]
    )
    if not countries:
        st.error("Please select at least one country.")
    else:
        if "All" in countries:
            countries = df.index

        new_df = df.loc[countries].reset_index()
        new_df = pd.melt(new_df, id_vars=["Country/Region"])
        new_df.columns = ["Country", "Date", "Deaths"]

        plot_history_data(new_df)
        st.write("you can zoom in on chart; double click to reset chart")
