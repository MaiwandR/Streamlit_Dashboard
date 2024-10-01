import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import matplotlib
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard", page_icon=":sunny:", layout ="wide")

st.title(":bar_chart: Streamlit Dashboard")

fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"Streamlit_Dashboard/Streamlit_Dashboard")
    df = pd.read_csv("Sample - Superstore.csv")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

#How ot get the range of dates for our data
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")
#Region

region = st.sidebar.multiselect("Pick the Region", df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]


#State: We filter based on the results of df2 and create a new filter named df3

state = st.sidebar.multiselect("Pick a State: ", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]


#City

city = st.sidebar.multiselect("Pick the City: ", df3["City"].unique())
if not state:
    df4 = df3.copy
else:
    df4 = df3[df3["City"].isin(city)]

#Filter data based on city, state, region
if not region and not state and not city:
    filter_df = df
elif not state and not city:
    filter_df = df[df["Region"].isin(region)]
elif not region and not city:
    filter_df = df[df["State"].isin(state)]
elif state and city:
    filter_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filter_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filter_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filter_df = df3[df3["City"].isin(city)]
else:
    filter_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


category_df = filter_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

colors = ['#7DCFB6', '#EF8354', '#C4455E', '#F1FFC4', '#F0C808','#9AC2C9', '#545775']
with col1:
    st.subheader(":money_with_wings: Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template= "seaborn", color='Category', color_discrete_sequence=colors)
    fig.update_traces(marker_line_color='rgba(0, 0, 0, 0)', marker_line_width=2)
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader(":pie: Region wise Sales")
    fig = px.pie(filter_df, values = "Sales", names = "Region", hole = 0.3)
    fig.update_traces(text = filter_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewDate"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime= "text/csv",
                           help = "Click here to download the data as a CSV file")

with cl2:
    with st.expander("Region_ViewDate"):
        region = filter_df.groupby(by = "Region", as_index = False )["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime= "text/csv",
                           help = "Click here to download the data as a CSV file")


filter_df["month_year"] = filter_df["Order Date"].dt.to_period("M")
st.subheader(':hourglass_flowing_sand: Time Series Analysis')

linechart = pd.DataFrame(filter_df.groupby(filter_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "Sales", labels = {"Sales": "Amount"}, height=500, width=1000, template="gridon", color_discrete_sequence=['#95E06C'])
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Bluyl"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="Time_Series_Analysis.csv", mime= "text/csv",
                       help="Click here to download the data as a CSV file")


#Creating a tree Map
st.subheader(":office: Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filter_df, path = ["Region", "Category", "Sub-Category"], values = "Sales", hover_data = ["Sales"],
                  color="Sub-Category", color_discrete_sequence=colors)
fig3.update_layout(width=800, height = 650)
st.plotly_chart(fig3, use_container_width=True)


chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filter_df, values = 'Sales', names="Segment", template="plotly_dark")
    fig.update_traces(text= filter_df["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


with chart2:
    st.subheader('Segment wise Sales')
    fig = px.pie(filter_df, values = 'Sales', names="Category", template="gridon")
    fig.update_traces(text= filter_df["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


import plotly.figure_factory as ff
st.subheader(":spiral_calendar_pad: Month wise Sub-Category Sales Summary")
with st.expander("Summary Table: "):
    df_sample = df[0:5][["Region", "State", "City", "Sales", "Category", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Tropic")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("Month wise Sub-category Table")
filter_df["month"] = filter_df["Order Date"].dt.month_name()
sub_category_Year = pd.pivot_table(data = filter_df, values="Sales", index=["Sub-Category"], columns="month")
st.write(sub_category_Year.style.background_gradient(cmap="Oranges"))

#Scatter plot creation
data1 = px.scatter(filter_df, x = "Sales", y = "Profit", size ="Quantity", color="Sales", color_continuous_scale="Bluyl")
data1['layout'].update(title="Relationship between Sales and Profit using Scatter Plot: ",
                       titlefont = dict(size=20), xaxis = dict(title= "Sales", titlefont = dict(size = 19)), 
                       yaxis = dict(title = "Profit", titlefont = dict(size = 19)))

st.plotly_chart(data1,use_container_width=True )


with st.expander("View Data"):
    st.write(filter_df.iloc[:500,1:20:2].style.background_gradient(cmap = "Reds"))

#Download Original
csv = df.to_csv(index = False).encode('utf-8')
st.download_button("Download Data", data = csv, file_name= "Original.csv", mime="text/csv")
