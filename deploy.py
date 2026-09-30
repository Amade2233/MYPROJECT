from utils import *


URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

df = get_data(URL, get_sunday_date)
df_day = prepare_data_day(df).to_frame()

forecast = make_forecast(df_day)
prev_50 = get_last_n_days_data(df_day, forecast=forecast)

st.title("Covid-19 Mortality Forecasting — West Africa")
st.caption(
    "MSc Data Analytics project · Technological University of the Shannon · "
    "Source: Johns Hopkins CSSE (dataset ceased updating March 2023)"
)

bar = st.sidebar
option = bar.selectbox(
    "Select an option", ("7-day death cases forecast", "death cases in West Africa"), 0
)

if option == "7-day death cases forecast":
    st.write("## A week forecast of death cases in West Africa")
    st.write("__ARIMA(1,1,3) forecast from the end of the available series__")

    plot_forecast(prev_50)
    st.write("you can zoom in on chart; double click to reset chart")
    st.write(f"### Total deaths forecast for the week is {forecast.sum()}")

if option == "death cases in West Africa":
    st.write("## Covid-19 death trend in West Africa by country")
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
