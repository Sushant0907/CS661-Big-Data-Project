import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import json
import os

#page configuration
st.set_page_config(
    page_title="Industrial Accidents Analysis",
    page_icon="🏭",
    layout="wide"
)

#loading data
@st.cache_data
def load_data():
    df = pd.read_csv('Indian_Industrial_Accidents.csv')
    return df


state_coordinates = {
    'Andhra Pradesh': {'lat': 15.9129, 'lon': 79.7400},
    'Karnataka': {'lat': 15.3173, 'lon': 75.7139},
    'Tamil Nadu': {'lat': 11.1271, 'lon': 78.6569},
    'Kerala': {'lat': 10.8505, 'lon': 76.2711},
    'Maharashtra': {'lat': 19.7515, 'lon': 75.7139},
    'Gujarat': {'lat': 22.2587, 'lon': 71.1924},
    'Rajasthan': {'lat': 27.0238, 'lon': 74.2179},
    'Uttar Pradesh': {'lat': 26.8467, 'lon': 80.9462},
    'Madhya Pradesh': {'lat': 22.9734, 'lon': 78.6569},
    'West Bengal': {'lat': 22.9868, 'lon': 87.8550},
    'Odisha': {'lat': 20.9517, 'lon': 85.0985},
    'Telangana': {'lat': 18.1124, 'lon': 79.0193},
    'Punjab': {'lat': 31.1471, 'lon': 75.3412},
    'Haryana': {'lat': 29.0588, 'lon': 76.0856},
    'Bihar': {'lat': 25.0961, 'lon': 85.3131},
    'Jharkhand': {'lat': 23.6102, 'lon': 85.2799},
    'Chhattisgarh': {'lat': 21.2787, 'lon': 81.8661},
    'Uttarakhand': {'lat': 30.0668, 'lon': 79.0193},
    'Himachal Pradesh': {'lat': 31.1048, 'lon': 77.1734},
    'Assam': {'lat': 26.2006, 'lon': 92.9376},
    'Goa': {'lat': 15.2993, 'lon': 74.1240}
}

#main func
def main():
    st.title("Industrial Accidents Analysis Dashboard")
    

    df = load_data()
    
    #filters
    st.sidebar.header("Filters")
    
    #state filters
    all_states = ['All'] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox('Select State', all_states)
    
    #accident Severity filter
    all_severities = ['All'] + sorted(df['Accident Severity'].unique().tolist())
    selected_severity = st.sidebar.selectbox('Select Accident Severity', all_severities)
    
    #apply filters
    if selected_state != 'All':
        df = df[df['State'] == selected_state]
    if selected_severity != 'All':
        df = df[df['Accident Severity'] == selected_severity]
    
    #creating tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Overview", "Temporal Analysis", "Geographic Analysis", 
        "Industry Analysis", "Demographic Analysis", "Risk Analysis",
        "Conclusions"
    ])
    
    #Overview
    with tab1:
        st.header("Overview")
        
        #summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Accidents", len(df))
        with col2:
            st.metric("Total States", df['State'].nunique())
        with col3:
            st.metric("Total Industry Sectors", df['Industry Sector'].nunique())
        
        #yearwise accidents
        st.subheader("Accidents by Year")
        year_counts = df['Year'].value_counts().sort_index()
        fig_year = px.bar(x=year_counts.index, y=year_counts.values, 
                         labels={'x': 'Year', 'y': 'Number of Accidents'},
                         title='Trend of Accidents Over Years',
                         color=year_counts.values,
                         color_continuous_scale='Viridis')
        st.plotly_chart(fig_year, use_container_width=True)
        
        #weekdays accidents
        st.subheader("Accidents by Day of Week")
        day_counts = df['DayOfWeek'].value_counts()
        fig_day = px.pie(values=day_counts.values, names=day_counts.index,
                        title='Distribution of Accidents by Day of Week',
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_day, use_container_width=True)
        
        #shiftwise accidents
        st.subheader("Accidents by Shift")
        shift_counts = df['Shift'].value_counts()
        fig_shift = px.bar(x=shift_counts.index, y=shift_counts.values,
                          labels={'x': 'Shift', 'y': 'Number of Accidents'},
                          title='Accidents Distribution by Shift',
                          color=shift_counts.index,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_shift, use_container_width=True)
        
        #state wise accidents
        st.subheader("Accidents by State")
        state_counts = df['State'].value_counts()
        

        map_data = []
        for state, count in state_counts.items():
            if state in state_coordinates:
                coords = state_coordinates[state]
                map_data.append({
                    'State': state,
                    'Accidents': count,
                    'Latitude': coords['lat'],
                    'Longitude': coords['lon']
                })
        
        map_df = pd.DataFrame(map_data)
        

        custom_colorscale = [
            [0.0, '#90EE90'], 
            [0.2, '#32CD32'], 
            [0.4, '#FFA500'],
            [0.6, '#FF6347'], 
            [0.8, '#DC143C'],  
            [1.0, '#8B0000'] 
        ]
        

        fig_state = go.Figure()
        

        full_df = load_data() 
        min_accidents = min(full_df['State'].value_counts())
        max_accidents = max(full_df['State'].value_counts())
        

        fig_state.add_trace(go.Scattermapbox(
            lat=map_df['Latitude'],
            lon=map_df['Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=map_df['Accidents'] * 5, 
                sizemode='area',
                sizeref=2.*max(map_df['Accidents'])/(5.**2),
                sizemin=5,  
                color=map_df['Accidents'],
                colorscale=custom_colorscale,
                cmin=min_accidents,  
                cmax=max_accidents,
                showscale=True,
                colorbar=dict(
                    title='Number of Accidents',
                    titleside='right',
                    len=0.5,  
                    y=0.5,   
                    thickness=15,  
                    x=1.1,   
                    xanchor='left' 
                ),
                opacity=0.8
            ),
            text=map_df['State'] + '<br>Accidents: ' + map_df['Accidents'].astype(str),
            hoverinfo='text',
            name='Accidents'
        ))
        
        #state filter applied
        if selected_state != 'All':
            selected_state_data = map_df[map_df['State'] == selected_state]
            if not selected_state_data.empty:
                fig_state.add_trace(go.Scattermapbox(
                    lat=selected_state_data['Latitude'],
                    lon=selected_state_data['Longitude'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=selected_state_data['Accidents'] * 7,
                        sizemode='area',
                        sizeref=2.*max(map_df['Accidents'])/(5.**2),
                        sizemin=7, 
                        color=selected_state_data['Accidents'],
                        colorscale=custom_colorscale,
                        cmin=min_accidents,
                        cmax=max_accidents,
                        opacity=1.0
                    ),
                    text=selected_state_data['State'] + '<br>Accidents: ' + selected_state_data['Accidents'].astype(str),
                    hoverinfo='text',
                    name='Selected State'
                ))
        
        fig_state.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=4,
            mapbox_center={"lat": 20.5937, "lon": 78.9629},
            margin={"r":100,"t":30,"l":0,"b":0}, 
            title='Accidents Distribution by State',
            showlegend=True
        )
        
        st.plotly_chart(fig_state, use_container_width=True)
        
        #ind sector accident
        st.subheader("Accidents by Industry Sector")
        sector_counts = df['Industry Sector'].value_counts()
        fig_sector = px.bar(x=sector_counts.index, y=sector_counts.values,
                           labels={'x': 'Industry Sector', 'y': 'Number of Accidents'},
                           title='Accidents Distribution by Industry Sector',
                           color=sector_counts.index,
                           color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_sector, use_container_width=True)
        
        #accident severity
        st.subheader("Accidents by Severity")
        severity_counts = df['Accident Severity'].value_counts()
        fig_severity = px.pie(values=severity_counts.values, names=severity_counts.index,
                             title='Distribution of Accident Severity',
                             hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_severity, use_container_width=True)
        
        # Accident Type
        st.subheader("Accidents by Type")
        type_counts = df['Accident Type'].value_counts()
        fig_type = px.bar(x=type_counts.index, y=type_counts.values,
                         labels={'x': 'Accident Type', 'y': 'Number of Accidents'},
                         title='Distribution of Accident Types',
                         color=type_counts.index,
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_type, use_container_width=True)
        
        # Gender distribution
        st.subheader("Accidents by Gender")
        gender_counts = df['Gender'].value_counts()
        fig_gender = px.pie(values=gender_counts.values, names=gender_counts.index,
                           title='Gender Distribution in Accidents',
                           color_discrete_sequence=['#FF9999', '#66B2FF'])
        st.plotly_chart(fig_gender, use_container_width=True)
        
        # Age distribution
        st.subheader("Accidents by Age")

        bins = list(range(18, 66, 5))
        labels = [f'{i}-{i+4}' for i in range(18, 61, 5)]
        df['Age Range'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
        age_counts = df['Age Range'].value_counts().sort_index()
        

        custom_age_colorscale = [
            [0.0, '#440154'], 
            [0.2, '#3B528B'],  
            [0.4, '#21918C'],  
            [0.6, '#5DC863'],  
            [0.8, '#FDE725'],  
            [1.0, '#FF0000']  
        ]
        
        fig_age = px.bar(x=age_counts.index, y=age_counts.values,
                        labels={'x': 'Age Range', 'y': 'Number of Accidents'},
                        title='Age Distribution of Accidents (Working Age)',
                        color=age_counts.values,
                        color_continuous_scale=custom_age_colorscale)
        st.plotly_chart(fig_age, use_container_width=True)
        
        # Employee Type
        st.subheader("Accidents by Employee Type")
        emp_counts = df['Employee Type'].value_counts()
        fig_emp = px.bar(x=emp_counts.index, y=emp_counts.values,
                        labels={'x': 'Employee Type', 'y': 'Number of Accidents'},
                        title='Accidents by Employee Type',
                        color=emp_counts.index,
                        color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig_emp, use_container_width=True)
        
        # Critical Risk 
        st.subheader("Accidents by Critical Risk")
        risk_counts = df['Critical Risk'].value_counts()
        fig_risk = px.bar(x=risk_counts.index, y=risk_counts.values,
                         labels={'x': 'Critical Risk', 'y': 'Number of Accidents'},
                         title='Distribution of Critical Risks',
                         color=risk_counts.index,
                         color_discrete_sequence=px.colors.qualitative.Dark24)
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Safety Gear 
        st.subheader("Accidents by Safety Gear")
        gear_counts = df['Safety Gear'].value_counts()
        fig_gear = go.Figure(data=[go.Pie(
            labels=gear_counts.index,
            values=gear_counts.values,
            hole=0.3,
            marker_colors=['#90EE90', '#8B0000'],  
            textinfo='label+percent',
            insidetextorientation='radial'
        )])
        fig_gear.update_layout(
            title='Safety Gear Usage in Accidents',
            showlegend=True
        )
        st.plotly_chart(fig_gear, use_container_width=True)
    
    # Temporal Analysis Tab
    with tab2:
        st.header("Temporal Analysis")
        

        st.subheader("Accidents by Year and Month")

        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']

        heatmap_data = df.pivot_table(index='Year', columns='Month', values='Accident Type', aggfunc='count')

        heatmap_data = heatmap_data[month_order]
        fig_heatmap = px.imshow(heatmap_data, 
                               labels=dict(x="Month", y="Year", color="Number of Accidents"),
                               title="Accident Frequency Heatmap by Year and Month",
                               color_continuous_scale=['yellow', 'red']) 
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Identifies seasonal patterns in accidents
        - Shows peak months for industrial accidents
        - Helps in planning preventive measures during high-risk periods
        """)
        
        #day of Week vs Shift Analysis
        st.subheader("Accidents by Day and Shift")
        pivot_data = df.pivot_table(index='DayOfWeek', columns='Shift', values='Accident Type', aggfunc='count')
        fig_pivot = px.imshow(pivot_data,
                             labels=dict(x="Shift", y="Day of Week", color="Number of Accidents"),
                             title="Accident Distribution by Day and Shift",
                             color_continuous_scale='Plasma')
        st.plotly_chart(fig_pivot, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Reveals most dangerous shift-day combinations
        - Helps in optimizing work schedules
        - Identifies patterns in shift-related accidents
        """)
        
        #Hour Type Distribution
        st.subheader("Accidents by Hour Type")

        total_accidents = len(df)
        hour_counts = df['Hour Type'].value_counts()
        hour_percentages = (hour_counts / total_accidents) * 100

        text_values = [f'{val:.1f}%' for val in hour_percentages.values]
        fig_hour = px.bar(x=hour_percentages.index, y=hour_percentages.values,
                         labels={'x': 'Hour Type', 'y': 'Percentage of Accidents (%)'},
                         title=f'Percentage Distribution of Accidents by Hour Type (Total: {total_accidents})',
                         color=hour_percentages.values,
                         color_continuous_scale='Inferno')

        fig_hour.update_traces(text=text_values, textposition='outside')
        st.plotly_chart(fig_hour, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the percentage distribution of accidents across different hour types
        - Percentages are calculated based on the currently filtered data
        - Helps in understanding the relative risk of different work hour categories
        """)
        
        #Yearly Trend with Severity
        st.subheader("Yearly Trend with Accident Severity")
        severity_trend = df.groupby(['Year', 'Accident Severity']).size().reset_index(name='Count')
        fig_severity_trend = px.line(severity_trend, x='Year', y='Count', color='Accident Severity',
                                   title='Trend of Accident Severity Over Years',
                                   markers=True)
        st.plotly_chart(fig_severity_trend, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Tracks changes in accident severity over time
        - Shows effectiveness of safety measures
        - Helps in evaluating safety program impact
        """)
        
        # Shift vs Severity Analysis
        st.subheader("Accidents by Shift & Severity")
        if not df.empty:
            shift_fig = px.histogram(df, x='Shift', color='Accident Severity', 
                                   barmode='group', 
                                   title='Distribution of Accidents by Shift and Severity',
                                   labels={'Shift': 'Shift', 'count': 'Number of Accidents'})
            shift_fig.update_layout(xaxis_title='Shift', yaxis_title='Number of Accidents')
            st.plotly_chart(shift_fig, use_container_width=True)
            st.markdown("""
            **Insights:**
            - Shows the distribution of accident severity across different shifts
            - Helps identify which shifts have higher proportions of severe accidents
            - Useful for shift-specific safety planning
            """)
        else:
            st.write("No data available for the selected filters.")
    
    # Geographic Analysis Tab
    with tab3:
        st.header("Geographic Analysis")
        
        #State vs Industry Sector
        st.subheader("State and Industry Sector Distribution")
        state_sector = df.groupby(['State', 'Industry Sector']).size().reset_index(name='Count')
        fig_state_sector = px.treemap(state_sector, path=['State', 'Industry Sector'], values='Count',
                                    title='Accident Distribution by State and Industry Sector',
                                    color='Count', color_continuous_scale='RdBu')
        st.plotly_chart(fig_state_sector, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows concentration of accidents by state and sector
        - Identifies high-risk state-industry combinations
        - Helps in targeted safety interventions
        """)
        
        #  Local Area Analysis
        st.subheader("Accidents by Local Area")
        local_counts = df['Local'].value_counts().head(10)
        fig_local = px.bar(x=local_counts.index, y=local_counts.values,
                          labels={'x': 'Local Area', 'y': 'Number of Accidents'},
                          title='Top 10 Local Areas with Most Accidents',
                          color=local_counts.values,
                          color_continuous_scale='Viridis')
        st.plotly_chart(fig_local, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Identifies high-risk local areas
        - Helps in local safety planning
        - Shows concentration of accidents in specific regions
        """)
        
        # State vs Accident Type
        st.subheader("State and Accident Type Distribution")
        state_type = df.groupby(['State', 'Accident Type']).size().reset_index(name='Count')
        fig_state_type = px.sunburst(state_type, path=['State', 'Accident Type'], values='Count',
                                   title='Accident Types Distribution by State',
                                   color='Count', color_continuous_scale='RdBu')
        st.plotly_chart(fig_state_type, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows prevalent accident types in each state
        - Helps in state-specific safety planning
        - Identifies regional patterns in accident types
        """)
    
    # Industry Analysis Tab
    with tab4:
        st.header("Industry Analysis")
        
        #Industry Sector vs Accident Type
        st.subheader("Industry Sector and Accident Type Analysis")
        sector_type = df.groupby(['Industry Sector', 'Accident Type']).size().reset_index(name='Count')
        fig_sector_type = px.sunburst(sector_type, path=['Industry Sector', 'Accident Type'], values='Count',
                                    title='Accident Types Distribution by Industry Sector',
                                    color='Count', color_continuous_scale='RdBu')
        st.plotly_chart(fig_sector_type, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows prevalent accident types in each industry
        - Helps in industry-specific safety planning
        - Identifies sector-specific risk patterns
        """)
        
        # Industry vs Critical Risk
        st.subheader("Industry and Critical Risk Analysis")
        sector_risk = df.groupby(['Industry Sector', 'Critical Risk']).size().reset_index(name='Count')
        fig_sector_risk = px.treemap(sector_risk, path=['Industry Sector', 'Critical Risk'], values='Count',
                                   title='Critical Risks Distribution by Industry Sector',
                                   color='Count', color_continuous_scale='RdBu')
        st.plotly_chart(fig_sector_risk, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows critical risks in each industry
        - Helps in targeted risk mitigation
        - Identifies industry-specific safety challenges
        """)
        
        # Industry vs Safety Gear Usage
        st.subheader("Industry and Safety Gear Usage")
        sector_gear = df.groupby(['Industry Sector', 'Safety Gear']).size().reset_index(name='Count')
        fig_sector_gear = px.bar(sector_gear, x='Industry Sector', y='Count', color='Safety Gear',
                               title='Safety Gear Usage by Industry Sector',
                               barmode='group')
        st.plotly_chart(fig_sector_gear, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows safety gear compliance by industry
        - Identifies industries needing safety gear enforcement
        - Helps in safety equipment planning
        """)
    
    # Demographic Analysis Tab
    with tab5:
        st.header("Demographic Analysis")
        
        #  Overall Gender Ratio (Pie Chart)
        st.subheader("Overall Gender Distribution")
        gender_counts = df['Gender'].value_counts()
        fig_gender_pie = px.pie(values=gender_counts.values, 
                              names=gender_counts.index,
                              title='Overall Gender Distribution in Accidents',
                              color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Blue for Male, Orange for Female
        st.plotly_chart(fig_gender_pie, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the overall proportion of accidents by gender
        - Helps understand gender distribution in industrial accidents
        - Provides baseline for gender-specific safety analysis
        """)
        
        # Gender Ratio with Filters (Bar Chart)
        st.subheader("Gender Distribution by Selected Filters")
        # Calculate gender distribution for current filters
        filtered_gender = df.groupby(['Gender']).size().reset_index(name='Count')
        filtered_gender['Percentage'] = (filtered_gender['Count'] / filtered_gender['Count'].sum()) * 100
        
        # Create title based on current filters
        filter_title = []
        if selected_state != 'All':
            filter_title.append(f"State: {selected_state}")
        if selected_severity != 'All':
            filter_title.append(f"Severity: {selected_severity}")
        title_suffix = " - " + " & ".join(filter_title) if filter_title else " (All Data)"
        
        fig_gender_bar = px.bar(filtered_gender,
                              x='Gender',
                              y='Percentage',
                              text=filtered_gender['Percentage'].round(1).astype(str) + '%',
                              title=f'Gender Distribution{title_suffix}',
                              color='Gender',
                              color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Blue for Male, Orange for Female
        fig_gender_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_gender_bar, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows gender distribution for the currently selected filters
        - Updates dynamically when state or severity filters change
        - Helps identify gender-specific patterns in different scenarios
        """)
        
        # Age vs Gender Distribution
        st.subheader("Age and Gender Distribution")
        age_gender = df.groupby(['Age Range', 'Gender']).size().reset_index(name='Count')
        fig_age_gender = px.bar(age_gender, x='Age Range', y='Count', color='Gender',
                              title='Accident Distribution by Age and Gender',
                              barmode='group')
        st.plotly_chart(fig_age_gender, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows age and gender patterns in accidents
        - Identifies vulnerable demographic groups
        - Helps in targeted safety training
        """)
        
        # Employee Type Analysis
        st.subheader("Accidents by Employee Type")
        emp_counts = df['Employee Type'].value_counts()
        fig_emp = px.bar(x=emp_counts.index, y=emp_counts.values,
                        labels={'x': 'Employee Type', 'y': 'Number of Accidents'},
                        title='Accident Distribution by Employee Type',
                        color=emp_counts.values,
                        color_continuous_scale='Viridis')
        st.plotly_chart(fig_emp, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows accident patterns by employee type
        - Identifies high-risk employee categories
        - Helps in employee-specific safety planning
        """)
        
        # Age vs Accident Type
        st.subheader("Age and Accident Type Analysis")
        age_type = df.groupby(['Age Range', 'Accident Type']).size().reset_index(name='Count')
        fig_age_type = px.bar(age_type, x='Age Range', y='Count', color='Accident Type',
                            title='Accident Types Distribution by Age',
                            barmode='group')
        st.plotly_chart(fig_age_type, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows prevalent accident types by age group
        - Helps in age-specific safety training
        - Identifies age-related risk patterns
        """)
    
    # Risk Analysis Tab
    with tab6:
        st.header("Risk Analysis")
        
        # Accident Type and Causes Analysis
        st.subheader("Accident Types and Their Causes")
        accident_causes = df.groupby(['Accident Severity', 'Accident Type']).size().reset_index(name='Count')
        fig_accident_causes = px.sunburst(accident_causes,
                                        path=['Accident Severity', 'Accident Type'],
                                        values='Count',
                                        title='Distribution of Accident Types by Severity',
                                        color='Count',
                                        color_continuous_scale='RdBu')
        st.plotly_chart(fig_accident_causes, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the distribution of different accident types by severity
        - Helps identify which types of accidents are most severe
        - Useful for prioritizing safety measures based on severity
        """)
        
        #  Safety Gear Effectiveness Analysis
        st.subheader("Safety Gear Effectiveness Analysis")
        safety_analysis = df.groupby(['Safety Gear', 'Accident Severity']).size().reset_index(name='Count')
        safety_analysis['Percentage'] = safety_analysis.groupby('Safety Gear')['Count'].transform(lambda x: x / x.sum() * 100)
        fig_safety = px.bar(safety_analysis,
                          x='Safety Gear',
                          y='Percentage',
                          color='Accident Severity',
                          title='Accident Severity Distribution with/without Safety Gear',
                          barmode='group',
                          text=safety_analysis['Percentage'].round(1).astype(str) + '%')
        fig_safety.update_traces(textposition='outside')
        st.plotly_chart(fig_safety, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the effectiveness of safety gear in preventing severe accidents
        - Demonstrates the importance of safety equipment usage
        - Helps in safety gear policy planning
        """)
        
        # Critical Risk vs. Accident Type
        st.subheader("Critical Risk and Accident Type Analysis")
        risk_type = df.groupby(['Critical Risk', 'Accident Type']).size().reset_index(name='Count')
        fig_risk_type = px.treemap(risk_type,
                                 path=['Critical Risk', 'Accident Type'],
                                 values='Count',
                                 title='Accident Types by Critical Risk',
                                 color='Count',
                                 color_continuous_scale='RdBu')
        st.plotly_chart(fig_risk_type, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows which critical risks lead to which types of accidents
        - Helps identify most dangerous risk factors
        - Useful for targeted risk mitigation
        """)
        
        # Time-based Risk Analysis
        st.subheader("Time-based Risk Analysis")
        time_risk = df.groupby(['DayOfWeek', 'Shift']).size().reset_index(name='Count')
        fig_time = px.density_heatmap(time_risk,
                                    x='DayOfWeek',
                                    y='Shift',
                                    z='Count',
                                    title='Accident Frequency by Day and Shift',
                                    color_continuous_scale='RdBu')
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Identifies high-risk time periods
        - Shows patterns in accident occurrence
        - Helps in shift planning and safety monitoring
        """)
        
        #  Age vs. Severity Analysis
        st.subheader("Age and Severity Analysis")
        age_severity = df.groupby(['Age Range', 'Accident Severity']).size().reset_index(name='Count')
        fig_age = px.bar(age_severity,
                        x='Age Range',
                        y='Count',
                        color='Accident Severity',
                        title='Accident Severity Distribution by Age Group',
                        barmode='stack')
        st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows which age groups are most vulnerable to severe accidents
        - Helps in age-specific safety training
        - Useful for targeted safety measures
        """)
        
        # Multiple Factor Risk Analysis
        st.subheader("Multiple Factor Risk Analysis")
        risk_factors = df.groupby(['Industry Sector', 'Critical Risk', 'Safety Gear']).size().reset_index(name='Count')
        fig_factors = px.parallel_categories(risk_factors,
                                          dimensions=['Industry Sector', 'Critical Risk', 'Safety Gear'],
                                          color='Count',
                                          title='Multiple Risk Factor Analysis',
                                          color_continuous_scale='RdBu')
        st.plotly_chart(fig_factors, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows complex interactions between multiple risk factors
        - Helps identify dangerous combinations of factors
        - Useful for comprehensive risk management
        """)
    
    # Conclusions Tab
    with tab7:
        st.header("Key Findings and Conclusions")
        
        st.subheader("Temporal Patterns")
        st.markdown("""
        - Peak accident periods identified
        - Shift and day patterns revealed
        - Seasonal variations in accident frequency
        - Yearly trends in accident severity
        """)
        
        st.subheader("Geographic Insights")
        st.markdown("""
        - High-risk states identified
        - State-industry combinations with most accidents
        - Local areas needing safety interventions
        - Geographic risk scores calculated
        """)
        
        st.subheader("Industry Analysis")
        st.markdown("""
        - Industry-specific risk patterns identified
        - Critical risks in each sector
        - Safety gear compliance by industry
        """)
        
        st.subheader("Demographic Findings")
        st.markdown("""
        - Age and gender patterns in accidents
        - Employee type specific risks
        - Demographic risk scores calculated
        """)
        
        st.subheader("Risk Management")
        st.markdown("""
        - Critical risk factors identified
        - Safety gear effectiveness analyzed
        - Risk mitigation strategies suggested
        - Comprehensive risk scoring system developed
        """)
        
        st.subheader("Recommendations")
        st.markdown("""
        1. Implement targeted safety programs for high-risk industries
        2. Focus on peak periods and shifts with most accidents
        3. Enhance safety gear compliance in identified sectors
        4. Develop age and experience-specific training programs
        5. Prioritize resources based on risk scores
        6. Regular safety audits in high-risk areas
        7. Continuous monitoring of safety measures effectiveness
        """)

if __name__ == "__main__":
    main() 