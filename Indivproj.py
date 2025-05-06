import streamlit as st 
import plotly.express as px 
import pandas as pd

# reading the data and making sure it works
web_link = "https://raw.githubusercontent.com/ywsjl/ProjLifeCW/refs/heads/main/CleanedGraduateEmployment.csv"
df = pd.read_csv(web_link)
degrees_avail = df["degree"].unique()
sel_year = df["year"].unique()
# Creating the sidebar
st.sidebar.title("Navigation")
navi = st.sidebar.radio("Go to:", ["Overview","Employment Success & Salary Trends","Key Insights"])

st.sidebar.title("Filters")
degrees_selected = st.sidebar.multiselect("Choose 1 or up to 5 degrees for comparison", degrees_avail)
uni_selection = st.sidebar.multiselect("Select universities", ["Nanyang Technological University", "National University of Singapore", "Singapore Management University", "Singapore Institute of Technology", "Singapore University of Social Sciences"])



# University lontitude and lagtitude
uni_loc = {
    "Uni": ["Nanyang Technological University", "National University of Singapore", "Singapore Management University", "Singapore Institute of Technology", "Singapore University of Social Sciences"],
    "Longitude":[103.6831,103.7764,103.8492,103.9316,103.9639],
    "Latitude": [1.3483,1.2966,1.2976,1.3541,1.3411]
}
uni_locations = pd.DataFrame(uni_loc)

# creating a function to read the coordinates input to create the map in overview 
def uni_map(loc_data):
    fig = px.scatter_mapbox(uni_locations, lat = "Latitude", lon = "Longitude", hover_name = "Uni", zoom = 11, color_discrete_sequence = ["red"] )
    fig.update_layout(mapbox_style = "open-street-map")
    return fig 

def Overview():
    st.header("Overview")
    st.subheader("List Of Degrees Available ")
    degree_opt = pd.DataFrame(df["degree"].unique(), columns = ["Degree"])
    st.dataframe(degree_opt)

    #Creating the map to show the location of all 5 universities
    st.subheader("University Locations")
    map = uni_map(uni_locations)
    st.plotly_chart(map, use_container_width = True)
    st.caption(f"""Foot Notes:\n
(*) SMU's courses are direct four-yr programmes and graduates could be awarded Cum Laude and above, Merit, High Merit or no awards. The data for SMU's courses is displayed in two categories: (i) overall results for all graduates within the course regardless of the award they attained, and (ii) results for the graduates awarded Cum Laude and above. Should the graduates undertake more than one Degree (e.g. Dual Degree programme), they have been classified based on their first Degree.\n
^ Data is based on a sample size of fewer than 30 respondents.\n
** No data is shown due to the small number of graduates and/or low response rates.\n
(#) Data on Law, Medical, Pharmacy and Biomedical Sciences & Chinese Medicine graduates are obtained from a follow-up survey on those who graduated one year ago (e.g. for 2018 GES survey, data is obtained from 2017 graduates) after they have completed their one-year practical law course/pupillage/housemanship/first-year residency/practical training. Data on Architecture graduates are obtained from a follow-up survey on those who graduated 3 years ago (e.g. for 2018 GES survey, data is obtained from 2015 graduates) after they have completed their practical training.\n
^^ Data includes the employment figures of graduates from Bachelor of Engineering (Bioengineering), which was merged into Bachelor of Engineering (Biomedical Engineering) in 2014.\n
(##) Data on NTU’s Medicine graduates will be obtained from a follow-up survey on the graduates after they have completed their housemanship/first-year residency.\n
(###) Data on SUTD's Bachelor of Science (Architecture and Sustainable Design) graduates will be obtained from a follow-up survey on the graduates after they have completed their practical training.""")



def EmpAndSalary():
    # a different ver of the year filter 
    year_sel = st.selectbox("Select year to view bar chart ranking the employment rate of your degree selections:", sorted(sel_year, reverse = True))
    
    # filtering the df so that the year and degrees selected appear
    filtered_df = df[(df["year"] == year_sel)]
    if len (degrees_selected) > 0:
        filtered_df = filtered_df[(filtered_df["degree"].isin(degrees_selected))]
        # sorting the df 
        sorted_df = filtered_df.sort_values(by = "employment_rate_overall", ascending = False).drop_duplicates(subset = "degree", keep = "first")
        fig_bar = px.bar(
            sorted_df,
            x = "degree", y = "employment_rate_overall",
            title = f"Overall Employment Rate Ranking for Selected Degrees ({year_sel})",
            hover_data = ["university"], 
            labels = {"employment_rate_overall": "Overall Employment Rate", "degree": "Degree"}
        )
        fig_bar.update_layout (xaxis_tickangle = -45)
        st.plotly_chart(fig_bar)
        # have to redo df for years as the above code filters the df to year user selects
    else:
        filtered_df = filtered_df.sort_values(by = "employment_rate_overall", ascending = False).head(5)
        fig_bar = px.bar(
            filtered_df,
            x = "degree", y = "employment_rate_overall",
            title = f"Overall Employment Rate Ranking for {year_sel}",
            hover_data= ["university"],
            labels = {"employment_rate_overall": "Overall Employment Rate", "degree": "Degree"}
        )
        fig_bar.update_layout (xaxis_tickangle = -45)
        st.plotly_chart(fig_bar)

    if len (degrees_selected) > 0:
        df_years = df[(df["degree"].isin(degrees_selected))]
        fig_line = px.line(
            df_years.sort_values("year"),
            x = "year",
            y = "gross_monthly_mean",
            markers = True,
            color = "degree",
            title = "Salary Over the Years per Degree",
            labels = {
                "year": "Year",
                "gross_monthly_mean": "Gross Monthly Mean ($)",                    
                "degree": "Degree"
                }
            )
        fig_line.update_layout (xaxis = dict(dtick = 1))
        st.plotly_chart(fig_line)
    else:
        # getting the top 5 degrees
        df_top5Deg = filtered_df.sort_values(by = "employment_rate_overall", ascending = False).drop_duplicates(subset = "degree").head(5)["degree"].tolist()
        df_years = df[df["degree"].isin(df_top5Deg)]
        fig_line = px.line(
            df_years.sort_values("year"),
            x = "year",
            y = "gross_monthly_mean",
            markers = True,
            color = "degree",
            title = "Salary Over the Years per Degree",
            labels = {
                "year": "Year",
                "gross_monthly_mean": "Gross Monthly Mean ($)",
                "degree": "Degree"
            }
        )
        fig_line.update_layout (xaxis = dict(dtick = 1))
        st.plotly_chart(fig_line)
                   


def KeyInsights():
    #Allowing user to view top 5 highest salary per year within the universities selected
    st.subheader("Degree with Highest Salary (Per Year)")
    st.caption("Filter Universities & Year Range")
    # Since im using a slider for year range I have to do my year again to get the earliest and latest year
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.sidebar.slider("Select Year Range:", min_value = min_year, max_value = max_year, value = (min_year,max_year))

    # Filter df by year range and universities selected
    filtered_df = df[
        (df["year"] >= year_range[0]) &
        (df["year"] <= year_range[1]) &
        (df["university"].isin(uni_selection))
    ]
    # Pull the highest paying degree and plot the chart
    sal_per_year = (
        filtered_df.sort_values(by = "gross_monthly_mean", ascending = False).drop_duplicates(subset = "year", keep = "first").sort_values(by = "year")
    )

    fig_bar = px.bar(
        sal_per_year,
        x = "year",
        y = "gross_monthly_mean",
        hover_data = ["degree", "university"],
        text = "degree",
        title = "Highest Paying Degree per Year & Universities of Choice",
        labels = {"gross_monthly_mean": "Gross Monthly Mean ($)", "year": "Year"}
    )

    fig_bar.update_traces(textposition = "outside")
    st.plotly_chart(fig_bar)

    st.markdown("The data reveals a significant shift in employment prospects, with Bachelor of Computing (Computer Science/Engineering) now surpassing Bachelor of Science with Honours programs. This rise in CS graduate employability directly correlates with Singapore's aggressive tech sector expansion. The government's Smart Nation initiative, together with increasing digital transformation across industries, has created demand for computing expertise. This trend reflects a fundamental economic realignment rather than a temporary fluctuation, suggesting continued strong employment prospects for computing graduates as Singapore positions itself as Southeast Asia's technology hub.")

    # stating the year range for me to compare the fastest growing salaray over the past 5 years
    #user won't be slecting the year range
    growth_year = 5
    latest_year = 2023
    earliest_year = latest_year - growth_year

    # filter the data 
    filtered_df = df[df["year"].isin([earliest_year,latest_year])]
    
    #grouping by degrees and year to calculate average salary
    avg_sal_per_degree = filtered_df.groupby(["degree","year"])["gross_monthly_mean"].mean().reset_index()
    pivot = avg_sal_per_degree.pivot(index = "degree", columns = "year", values = ["gross_monthly_mean"])
    #rename the columns
    pivot.columns = ["Salary (2018)", "Salary (2023)"]
    #calc the growth to plot chart
    pivot["absolute_growth"] = pivot["Salary (2023)"] - pivot["Salary (2018)"]
    pivot ["percentage_growth"] = (pivot["absolute_growth"]/pivot["Salary (2018)"]) * 100

    top5 = pivot.sort_values("percentage_growth", ascending = False).head(5)

    st.subheader(f"Top 5 Degrees with Highest Salary growth ({earliest_year} to {latest_year})")
    st.dataframe(top5.reset_index())
    st.markdown("The salary progression analysis reveals compelling evidence of Singapore's tech-driven economic transformation. Computing graduates have experienced a 42-45% increase in average gross starting monthly income between 2018 and 2023. This dramatic salary acceleration directly reflects the intensifying competition for computing talent as organisations across all sectors pursue digital transformation initiatives. With the government's continued investment in digital infrastructure and Smart Nation priorities, this premium on technology skills shows no signs of slowing down.")

if navi == "Employment Success & Salary Trends":
    st.header("Employment Success & Salary Trends")
    EmpAndSalary()
elif navi == "Overview":
    Overview()
else:
    st.header("Key Insights")
    KeyInsights()







