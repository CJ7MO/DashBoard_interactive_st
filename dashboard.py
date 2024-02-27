import os
import warnings

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Super Store!", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Super Store EDA :chart_with_upwards_trend:")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xslx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_excel(filename)
else:
    df = pd.read_excel("Sample - Superstore.xls")

col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"])

# Getting the min and max date
start_date = pd.to_datetime(df["Order Date"]).min()
end_date = pd.to_datetime(df["Order Date"]).max()

with col1:
    date_1 = pd.to_datetime(st.date_input("Start Date: ", start_date))

with col2:
    date_2 = pd.to_datetime(st.date_input("End Date: ", end_date))

df = df[(df["Order Date"] >= date_1) & (df["Order Date"] <= date_2)].copy()

st.sidebar.header("Choose your filter: ")

# Create for Region
region = st.sidebar.multiselect("Pick Your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Create for State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Create for City
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())
if not city:
    df4 = df.copy()
else:
    df4 = df3[df3["City"].isin(city)]

# Filter the data based on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not state:
    filtered_df = df[df["City"].isin(city)]
elif not city and not region:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df[df["City"].isin(city)]
else:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state) & df["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
region_df = filtered_df.groupby(by=["Region"], as_index=False)["Sales"].sum()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

col_1, col_2 = st.columns(2)
with col_1:
    with st.expander("Category View Data"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('UTF-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help="Click here to download the data as CSV file", key="category")
with col_2:
    with st.expander("Region View Data"):
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('UTF-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help="Click here to download the data as CSV file", key="region")

# Asegúrate de tener 'Order Date' como tipo de dato de fecha y hora (datetime)
filtered_df["Order Date"] = pd.to_datetime(filtered_df["Order Date"])

# Ordena el DataFrame por la columna 'Order Date'
filtered_df = filtered_df.sort_values(by="Order Date")

# Crea el DataFrame para el gráfico de líneas
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["Order Date"].dt.to_period("M").dt.strftime("%Y-%m-%B"))[
                             "Sales"].sum().reset_index())

# Crea el gráfico de líneas
fig2 = px.line(linechart, x="Order Date", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000,
               template="gridon")

# Muestra el gráfico en Streamlit
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of Time Series: "):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("UTF-8")
    st.download_button("Download Data", data=csv, file_name="Time_Series.csv", mime="text/csv",
                       help="Click here to download the data as CSV file", key="time_series")

# Create a tree map based on Region, Category, sub-Category
st.subheader("Hierarchical view of Sales using Tree Map")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart_1, chart_2 = st.columns(2)

with chart_1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart_2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="seaborn")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table: "):
    df_sample = df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head()
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(":date: Month wise Sub-Category Table")
with st.expander("View Data"):
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"), use_container_width=True)

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1["layout"].update(title="Relationship between Sales and Profits Using Scatter Plot",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=17)),
                       yaxis=dict(title="Profit", titlefont=dict(size=17)))

st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"), use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download entire data", data=csv, file_name="data.csv", mime="text/csv")
