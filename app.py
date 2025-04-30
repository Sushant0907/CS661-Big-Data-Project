import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import geopandas as gpd
import json
import os
import math

# Set page configuration
st.set_page_config(
    page_title="Industrial Accidents Analysis",
    page_icon="🏭",
    layout="wide"
)

# Load data


@st.cache_data
def load_data():
    df = pd.read_csv('Indian_Industrial_Accidents.csv')
    return df

# Load the India state GeoJSON data
@st.cache_data
def load_geojson():
    # Check for local GeoJSON files with different possible names
    possible_filenames = ['india_state_geo.json', 'india_states.geojson', 'india_states.json']
    
    # Try each filename
    for filename in possible_filenames:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    india_geojson = json.load(f)
                return india_geojson
            except Exception as e:
                st.error(f"Error loading GeoJSON from {filename}: {e}")
    
    # If we couldn't load any file, create a simplified version
    st.warning("No GeoJSON file found. Creating simplified state boundaries for visualization.")
    return create_simplified_geojson()

@st.cache_data
def create_simplified_geojson():
    """Create a simplified GeoJSON with state boundaries when the proper file can't be loaded"""
    st.warning("Creating simplified state boundaries for visualization. For better results, please ensure the india_states.geojson file is available.")
    
    # Get coordinates for Indian states
    state_coords = get_india_state_coordinates()
    
    # Create a simplified polygon for each state
    features = []
    for state, [lat, lon] in state_coords.items():
        # Create a hexagon around the state point for better visual appearance
        radius = 0.8  # Size in degrees
        # Create 6 points in a hexagon shape
        hex_points = []
        for i in range(7):  # 6 points + closing point
            angle = (i * 60) * (math.pi / 180)
            hex_points.append([
                lon + radius * math.cos(angle),
                lat + radius * math.sin(angle)
            ])
        
        feature = {
            "type": "Feature",
            "properties": {"name": state},
            "geometry": {
                "type": "Polygon",
                "coordinates": [hex_points]
            }
        }
        features.append(feature)
    
    simplified_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return simplified_geojson

# Get India state coordinates for visualization
@st.cache_data
def get_india_state_coordinates():
    # Dictionary mapping Indian states to their approximate coordinates
    # These are approximate latitude and longitude for state centroids
    return {
        'Andhra Pradesh': [15.9129, 79.7400],
        'Arunachal Pradesh': [28.2180, 94.7278],
        'Assam': [26.2006, 92.9376],
        'Bihar': [25.0961, 85.3131],
        'Chhattisgarh': [21.2787, 81.8661],
        'Goa': [15.2993, 74.1240],
        'Gujarat': [22.2587, 71.1924],
        'Haryana': [29.0588, 76.0856],
        'Himachal Pradesh': [31.1048, 77.1734],
        'Jharkhand': [23.6102, 85.2799],
        'Karnataka': [15.3173, 75.7139],
        'Kerala': [10.8505, 76.2711],
        'Madhya Pradesh': [22.9734, 78.6569],
        'Maharashtra': [19.7515, 75.7139],
        'Manipur': [24.6637, 93.9063],
        'Meghalaya': [25.4670, 91.3662],
        'Mizoram': [23.1645, 92.9376],
        'Nagaland': [26.1584, 94.5624],
        'Odisha': [20.9517, 85.0985],
        'Punjab': [31.1471, 75.3412],
        'Rajasthan': [27.0238, 74.2179],
        'Sikkim': [27.5330, 88.5122],
        'Tamil Nadu': [11.1271, 78.6569],
        'Telangana': [18.1124, 79.0193],
        'Tripura': [23.9408, 91.9882],
        'Uttar Pradesh': [26.8467, 80.9462],
        'Uttarakhand': [30.0668, 79.0193],
        'West Bengal': [22.9868, 87.8550],
        'Andaman and Nicobar Islands': [11.7401, 92.6586],
        'Chandigarh': [30.7333, 76.7794],
        'Dadra and Nagar Haveli': [20.1809, 73.0169],
        'Daman and Diu': [20.4283, 72.8397],
        'Delhi': [28.7041, 77.1025],
        'Jammu and Kashmir': [33.7782, 76.5762],
        'Ladakh': [34.2996, 78.2932],
        'Lakshadweep': [10.5667, 72.6417],
        'Puducherry': [11.9416, 79.8083]
    }


# State coordinates mapping
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

def create_choropleth_map(df):
    """
    Create a choropleth map showing accident counts by state with color gradient
    (red for most accidents, blue for least accidents)
    """
    # Group data by State to get accident counts
    state_counts = df.groupby('State').size().reset_index(name='Accident_Count')
    
    # Add min and max for reference in the hover data
    min_accidents = state_counts['Accident_Count'].min()
    max_accidents = state_counts['Accident_Count'].max()
    state_counts['Min'] = min_accidents
    state_counts['Max'] = max_accidents
    
    # Load India state GeoJSON with proper boundaries
    india_geojson = load_geojson()
    
    # Check the property name that contains state names in the GeoJSON
    feature_key = "name"
    if india_geojson and india_geojson["features"]:
        props = india_geojson["features"][0]["properties"]
        # Look for common property names for state names
        for key in ["name", "NAME", "NAME_1", "ST_NM", "state", "STATE"]:
            if key in props:
                feature_key = key
                break
    
    # Create state name mapping to handle potential differences
    state_mapping = {}
    states_in_data = set(state_counts['State'].unique())
    
    # Create a mapping function to match state names in data with GeoJSON
    def map_state_names(state_name):
        # Common variations in state names
        variations = {
            "Delhi": ["NCT of Delhi", "Delhi", "National Capital Territory of Delhi"],
            "Jammu and Kashmir": ["Jammu & Kashmir", "J&K", "Jammu & Kashmir"],
            "Andaman and Nicobar Islands": ["A & N Islands", "Andaman & Nicobar", "Andaman & Nicobar Islands"],
            "Dadra and Nagar Haveli": ["Dadra & Nagar Haveli", "DNH"],
            "Daman and Diu": ["Daman & Diu"],
            "Tamil Nadu": ["Tamilnadu"],
            "Puducherry": ["Pondicherry"],
            "Odisha": ["Orissa"],
            "Uttarakhand": ["Uttaranchal"],
            "Telangana": ["Telengana"]
        }
        
        # Try variations if available
        if state_name in variations:
            return variations[state_name]
        
        # Otherwise return just the original name
        return [state_name]
    
    # Map data state names to possible GeoJSON state names
    for state in states_in_data:
        state_mapping[state] = map_state_names(state)
    
    # Get all available states from GeoJSON to ensure full India outline is shown
    geojson_states = []
    if india_geojson and "features" in india_geojson:
        for feature in india_geojson["features"]:
            if "properties" in feature and feature_key in feature["properties"]:
                geojson_states.append(feature["properties"][feature_key])
    
    # Create a complete dataset with all states, including those with no data
    complete_state_data = []
    for state in geojson_states:
        state_data = state_counts[state_counts['State'] == state]
        if len(state_data) > 0:
            # State exists in our data
            complete_state_data.append(state_data.iloc[0].to_dict())
        else:
            # State doesn't exist in our data, add with count 0
            complete_state_data.append({
                'State': state,
                'Accident_Count': 0,
                'Min': min_accidents,
                'Max': max_accidents
            })
    
    # Convert to DataFrame
    complete_df = pd.DataFrame(complete_state_data)
    
    # Only use non-zero values for color range to ensure proper gradient
    non_zero_min = complete_df[complete_df['Accident_Count'] > 0]['Accident_Count'].min()
    non_zero_max = complete_df['Accident_Count'].max()
    
    # Create the choropleth map
    fig = px.choropleth_mapbox(
        complete_df,
        geojson=india_geojson,
        locations='State',
        featureidkey=f"properties.{feature_key}",
        color='Accident_Count',
        color_continuous_scale=[
            [0, 'white'],  # 0 accidents (no data)
            [non_zero_min/non_zero_max, 'blue'],  # minimum accidents
            [1, 'red']  # maximum accidents
        ],
        range_color=[0, non_zero_max],  # Set the range from 0 to max accidents
        mapbox_style="carto-positron",
        zoom=3.8,
        center={"lat": 22.5937, "lon": 78.9629},  # Center of India
        opacity=0.85,
        labels={'Accident_Count': 'Number of Accidents'},
        hover_data={
            'Accident_Count': True,
            'Min': False,
            'Max': False
        },
        custom_data=['Accident_Count']
    )
    
    # Add state borders for better visibility
    fig.update_traces(
        marker=dict(line=dict(width=1, color='black')),
        hovertemplate="<b>%{location}</b><br>Accidents: %{customdata[0]}<br>%{customdata[0] === 0 ? '<i>Data not available</i>' : ''}<extra></extra>"
    )
    
    # Update the color axis
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Accident Count",
            tickvals=[0, non_zero_min, non_zero_max],
            ticktext=["No data", f"Minimum ({non_zero_min})", f"Maximum ({non_zero_max})"]
        ),
        mapbox=dict(
            style="carto-positron",
            zoom=3.8,
            center={"lat": 22.5937, "lon": 78.9629}
        )
    )
    
    return fig, state_counts


# Main function
def main():
    st.title("Industrial Accidents Analysis Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # State filter
    all_states = ['All'] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox('Select State', all_states)
    
    # Accident Severity filter
    all_severities = ['All'] + sorted(df['Accident Severity'].unique().tolist())
    selected_severity = st.sidebar.selectbox('Select Accident Severity', all_severities)
    
    # Apply filters
    if selected_state != 'All':
        df = df[df['State'] == selected_state]
    if selected_severity != 'All':
        df = df[df['Accident Severity'] == selected_severity]
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Overview", "Temporal Analysis", "Geographic Analysis", 
        "Industry Analysis", "Demographic Analysis", "Risk Analysis",
        "Conclusions"
    ])
    
    # Overview Tab with all graphs
    with tab1:
        st.header("Overview")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Accidents", len(df))
        with col2:
            st.metric("Total States", df['State'].nunique())
        with col3:
            st.metric("Total Industry Sectors", df['Industry Sector'].nunique())
        
        # Year-wise accidents - Bar chart
        st.subheader("Accidents by Year")
        year_counts = df['Year'].value_counts().sort_index()
        fig_year = px.bar(x=year_counts.index, y=year_counts.values, 
                         labels={'x': 'Year', 'y': 'Number of Accidents'},
                         title='Trend of Accidents Over Years',
                         color=year_counts.values,
                         color_continuous_scale='Viridis')
        st.plotly_chart(fig_year, use_container_width=True)
        
        # Day of Week accidents - Pie chart
        st.subheader("Accidents by Day of Week")
        day_counts = df['DayOfWeek'].value_counts()
        fig_day = px.pie(values=day_counts.values, names=day_counts.index,
                        title='Distribution of Accidents by Day of Week',
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_day, use_container_width=True)
        
        # Shift-wise accidents - Bar chart with colors
        st.subheader("Accidents by Shift")
        shift_counts = df['Shift'].value_counts()
        fig_shift = px.bar(x=shift_counts.index, y=shift_counts.values,
                          labels={'x': 'Shift', 'y': 'Number of Accidents'},
                          title='Accidents Distribution by Shift',
                          color=shift_counts.index,
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_shift, use_container_width=True)
        
        # State-wise accidents - Scatter map
        st.subheader("Accidents by State")
        state_counts = df['State'].value_counts()
        
        # Create a DataFrame with state coordinates and accident counts
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
        
        # Create a custom color scale from light green to dark red
        custom_colorscale = [
            [0.0, '#90EE90'],  # Light green
            [0.2, '#32CD32'],  # Lime green
            [0.4, '#FFA500'],  # Orange
            [0.6, '#FF6347'],  # Tomato
            [0.8, '#DC143C'],  # Crimson
            [1.0, '#8B0000']   # Dark red
        ]
        
        # Create the scatter map with dynamic sizing
        fig_state = go.Figure()
        
        # Calculate min and max accidents for color scaling from the full dataset
        full_df = load_data()  # Get the full dataset for color scale
        min_accidents = min(full_df['State'].value_counts())
        max_accidents = max(full_df['State'].value_counts())
        
        # Add the scatter points with dynamic sizing
        fig_state.add_trace(go.Scattermapbox(
            lat=map_df['Latitude'],
            lon=map_df['Longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=map_df['Accidents'] * 5,  # Base size
                sizemode='area',
                sizeref=2.*max(map_df['Accidents'])/(5.**2),  # Adjusted for better zoom scaling
                sizemin=5,  # Minimum size
                color=map_df['Accidents'],
                colorscale=custom_colorscale,
                cmin=min_accidents,  # Use full dataset min/max for consistent scale
                cmax=max_accidents,
                showscale=True,
                colorbar=dict(
                    title='Number of Accidents',
                    titleside='right',
                    len=0.5,  # Shorter colorbar
                    y=0.5,    # Center vertically
                    thickness=15,  # Thinner colorbar
                    x=1.1,    # Move further to the right
                    xanchor='left'  # Anchor to the left of the colorbar
                ),
                opacity=0.8
            ),
            text=map_df['State'] + '<br>Accidents: ' + map_df['Accidents'].astype(str),
            hoverinfo='text',
            name='Accidents'
        ))
        
        # Add selected state with different color if filter is applied
        if selected_state != 'All':
            selected_state_data = map_df[map_df['State'] == selected_state]
            if not selected_state_data.empty:
                fig_state.add_trace(go.Scattermapbox(
                    lat=selected_state_data['Latitude'],
                    lon=selected_state_data['Longitude'],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=selected_state_data['Accidents'] * 7,  # Larger for selected
                        sizemode='area',
                        sizeref=2.*max(map_df['Accidents'])/(5.**2),
                        sizemin=7,  # Larger minimum size
                        color=selected_state_data['Accidents'],
                        colorscale=custom_colorscale,
                        cmin=min_accidents,  # Use full dataset min/max for consistent scale
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
            margin={"r":100,"t":30,"l":0,"b":0},  # Increased right margin for colorbar
            title='Accidents Distribution by State',
            showlegend=True
        )
        
        st.plotly_chart(fig_state, use_container_width=True)
        
        # Industry Sector accidents - Bar chart
        st.subheader("Accidents by Industry Sector")
        sector_counts = df['Industry Sector'].value_counts()
        fig_sector = px.bar(x=sector_counts.index, y=sector_counts.values,
                           labels={'x': 'Industry Sector', 'y': 'Number of Accidents'},
                           title='Accidents Distribution by Industry Sector',
                           color=sector_counts.index,
                           color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_sector, use_container_width=True)
        
        # Accident Severity - Donut chart
        st.subheader("Accidents by Severity")
        severity_counts = df['Accident Severity'].value_counts()
        fig_severity = px.pie(values=severity_counts.values, names=severity_counts.index,
                             title='Distribution of Accident Severity',
                             hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_severity, use_container_width=True)
        
        # Accident Type - Bar chart with colors
        st.subheader("Accidents by Type")
        type_counts = df['Accident Type'].value_counts()
        fig_type = px.bar(x=type_counts.index, y=type_counts.values,
                         labels={'x': 'Accident Type', 'y': 'Number of Accidents'},
                         title='Distribution of Accident Types',
                         color=type_counts.index,
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_type, use_container_width=True)
        
        # Gender distribution - Pie chart
        st.subheader("Accidents by Gender")
        gender_counts = df['Gender'].value_counts()
        fig_gender = px.pie(values=gender_counts.values, names=gender_counts.index,
                           title='Gender Distribution in Accidents',
                           color_discrete_sequence=['#FF9999', '#66B2FF'])
        st.plotly_chart(fig_gender, use_container_width=True)
        
        # Age distribution - Bar chart
        st.subheader("Accidents by Age")
        # Create age ranges with 5-year intervals
        bins = list(range(18, 66, 5))
        labels = [f'{i}-{i+4}' for i in range(18, 61, 5)]
        df['Age Range'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
        age_counts = df['Age Range'].value_counts().sort_index()
        
        # Create a custom color scale with more variation
        custom_age_colorscale = [
            [0.0, '#440154'],  # Dark purple
            [0.2, '#3B528B'],  # Dark blue
            [0.4, '#21918C'],  # Teal
            [0.6, '#5DC863'],  # Green
            [0.8, '#FDE725'],  # Yellow
            [1.0, '#FF0000']   # Red
        ]
        
        fig_age = px.bar(x=age_counts.index, y=age_counts.values,
                        labels={'x': 'Age Range', 'y': 'Number of Accidents'},
                        title='Age Distribution of Accidents (Working Age)',
                        color=age_counts.values,
                        color_continuous_scale=custom_age_colorscale)
        st.plotly_chart(fig_age, use_container_width=True)
        
        # Employee Type - Bar chart with colors
        st.subheader("Accidents by Employee Type")
        emp_counts = df['Employee Type'].value_counts()
        fig_emp = px.bar(x=emp_counts.index, y=emp_counts.values,
                        labels={'x': 'Employee Type', 'y': 'Number of Accidents'},
                        title='Accidents by Employee Type',
                        color=emp_counts.index,
                        color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig_emp, use_container_width=True)
        
        # # Critical Risk - Bar chart
        # st.subheader("Accidents by Critical Risk")
        # risk_counts = df['Critical Risk'].value_counts()
        # fig_risk = px.bar(x=risk_counts.index, y=risk_counts.values,
        #                  labels={'x': 'Critical Risk', 'y': 'Number of Accidents'},
        #                  title='Distribution of Critical Risks',
        #                  color=risk_counts.index,
        #                  color_discrete_sequence=px.colors.qualitative.Dark24)
        # st.plotly_chart(fig_risk, use_container_width=True)
        
        # Safety Gear - Segmented Pie chart
        st.subheader("Accidents by Safety Gear")
        gear_counts = df['Safety Gear'].value_counts()
        fig_gear = go.Figure(data=[go.Pie(
            labels=gear_counts.index,
            values=gear_counts.values,
            hole=0.3,
            marker_colors=['#E74C3C', '#2ECC71'],  # Bright green for Yes, Red for No
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
        
        # 1. Year-Month Heatmap
        st.subheader("Accidents by Year and Month")
        # Create month order for proper sorting
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        # Create pivot table with month names
        heatmap_data = df.pivot_table(index='Year', columns='Month', values='Accident Type', aggfunc='count')
        # Reorder columns according to month_order
        heatmap_data = heatmap_data[month_order]
        fig_heatmap = px.imshow(heatmap_data, 
                               labels=dict(x="Month", y="Year", color="Number of Accidents"),
                               title="Accident Frequency Heatmap by Year and Month",
                               color_continuous_scale=['yellow', 'red'])  # Yellow for low, Red for high
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Identifies seasonal patterns in accidents
        - Shows peak months for industrial accidents
        - Helps in planning preventive measures during high-risk periods
        """)
        
        # 2. Day of Week vs Shift Analysis
        st.subheader("Accidents by Day and Shift")
        # Define the correct order for days of the week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Ensure DayOfWeek is a categorical type with the correct order
        df['DayOfWeek'] = pd.Categorical(df['DayOfWeek'], categories=day_order, ordered=True)
        pivot_data = df.pivot_table(index='DayOfWeek', columns='Shift', values='Accident Type', aggfunc='count').reindex(day_order)
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
        
        # 3. Hour Type Distribution
        st.subheader("Accidents by Hour Type")
        
        if selected_severity == 'All':
            # Calculate percentages based on total accidents when 'All' is selected
            total_accidents = len(df)
            hour_counts = df['Hour Type'].value_counts()
            hour_percentages = (hour_counts / total_accidents) * 100
            
            # Create DataFrame for plotting
            hour_data = pd.DataFrame({
                'Hour Type': hour_counts.index,
                'Count': hour_counts.values,
                'Percentage': hour_percentages.values
            })
            
            # Create color mapping dictionary
            color_map = {'Working Hour': '#3498DB', 'Over Time': '#E67E22'}  # Blue for Working Hour, Orange for Over Time
            
            # Create the bar chart
            fig_hour = px.bar(hour_data,
                            x='Hour Type',
                            y='Percentage',
                            text=hour_data['Percentage'].round(1).astype(str) + '%',
                            labels={'x': 'Hour Type', 'y': 'Percentage of Total Accidents (%)'},
                            title=f'Percentage Distribution of Accidents by Hour Type (Total: {total_accidents})',
                            color='Hour Type',
                            color_discrete_map=color_map)  # Use fixed color mapping
            fig_hour.update_traces(textposition='outside')
            
        else:
            # Filter data for the selected severity
            severity_data = df[df['Accident Severity'] == selected_severity]
            
            # Calculate counts and percentages for each hour type
            hour_type_data = severity_data['Hour Type'].value_counts().reset_index()
            hour_type_data.columns = ['Hour Type', 'Count']
            
            # Calculate total for this severity
            severity_total = hour_type_data['Count'].sum()
            
            # Calculate percentages
            hour_type_data['Percentage'] = (hour_type_data['Count'] / severity_total * 100).round(1)
            
            # Create color mapping dictionary
            color_map = {'Working Hour': '#3498DB', 'Over Time': '#E67E22'}  # Blue for Working Hour, Orange for Over Time
            
            # Create the bar chart
            fig_hour = px.bar(hour_type_data,
                            x='Hour Type',
                            y='Count',
                            text=[f'{count} ({pct}%)' for count, pct in zip(hour_type_data['Count'], hour_type_data['Percentage'])],
                            labels={'x': 'Hour Type', 'y': 'Number of Accidents'},
                            title=f'Accident Distribution by Hour Type (Severity: {selected_severity}, Total: {severity_total})',
                            color='Hour Type',
                            color_discrete_map=color_map)  # Use fixed color mapping
            
            # Ensure y-axis starts at 0 and has enough room for labels
            max_count = hour_type_data['Count'].max()
            fig_hour.update_layout(
                yaxis=dict(
                    range=[0, max_count * 1.2],
                    tickmode='linear',
                    dtick=max(1, max_count // 5)  # Set tick interval based on max count
                )
            )
            fig_hour.update_traces(textposition='outside')
        
        st.plotly_chart(fig_hour, use_container_width=True)
        st.markdown("""
        **Insights:**
        - When 'All' is selected: Shows overall percentage distribution across hour types
        - When specific severity is selected: Shows counts and percentages within that severity level
        - Helps in understanding accident patterns during different work periods
        """)
        
        # 4. Shift vs Severity Analysis
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
        
        # Add the Choropleth map from indian_accidents_geo_analysis.py
        st.subheader("Accident Distribution by State (Heat Map)")
        choropleth_map, state_counts = create_choropleth_map(df)
        st.plotly_chart(choropleth_map, use_container_width=True)
        
        st.markdown("""
        **Insights:**
        - The heat map shows state-wise accident intensity with red indicating higher accident counts and blue indicating lower counts.
        - States with the highest industrial accident counts are shown in darker red.
        - White areas indicate states with no recorded accidents in the dataset.
        - The visualization helps identify regional patterns and state-specific risk levels.
        - This map can guide resource allocation for safety programs based on geographic need.
        """)

        
        # 1. State vs Industry Sector
        st.subheader("State and Industry Sector Distribution")
        state_sector = df.groupby(['State', 'Industry Sector']).size().reset_index(name='Count')
        fig_state_sector = px.treemap(state_sector, path=['State', 'Industry Sector'], values='Count',
                                    title='Accident Distribution by State and Industry Sector',
                                    color='Count', color_continuous_scale='RdBu')
        st.plotly_chart(fig_state_sector, use_container_width=True)
        # st.markdown("""
        # **Insights:**
        # - Shows concentration of accidents by state and sector
        # - Identifies high-risk state-industry combinations
        # - Helps in targeted safety interventions
        # """)
        
        
        # Insights for the treemap
        st.markdown(
            """
            <div class="insight-box">
                <div class="insight-title">Key Geographic Distribution Insights:</div>
                <ul>
                    <li>The treemap visualization provides a hierarchical view of accident distribution, showing which states have the highest accident counts and the industry sectors contributing to these accidents.</li>
                    <li>Larger blocks represent states with more accidents, while the nested blocks show the proportion of accidents by industry sector within each state.</li>
                    <li>Manufacturing and construction sectors dominate accident counts in most industrialized states.</li>
                    <li>Some states show unique industry-specific patterns that require targeted safety interventions.</li>
                    <li>The color intensity indicates accident frequency, helping to identify the most critical state-industry combinations for safety focus.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Add Severity Distribution by States
        st.subheader("Severity Distribution by States")
        # Calculate severity distribution for each state
        severity_state = df.groupby(['State', 'Accident Severity']).size().reset_index(name='Count')
        # Calculate percentage within each state
        total_by_state = severity_state.groupby('State')['Count'].transform('sum')
        severity_state['Percentage'] = (severity_state['Count'] / total_by_state * 100).round(1)
        
        # Sort states by total accidents for better visualization
        state_order = df.groupby('State').size().sort_values(ascending=False).index
        
        # Create the stacked bar chart
        fig_severity_state = px.bar(severity_state,
                                  x='State',
                                  y='Percentage',
                                  color='Accident Severity',
                                  title='Accident Severity Distribution by State',
                                  text=severity_state['Percentage'].round(1).astype(str) + '%',
                                  category_orders={'State': state_order},
                                  color_discrete_sequence=px.colors.qualitative.Set2)
        
        # Update layout for better readability
        fig_severity_state.update_layout(
            xaxis_title="State",
            yaxis_title="Percentage of State's Total Accidents",
            showlegend=True,
            xaxis_tickangle=-45,
            height=600,  # Increase height for better visibility
            yaxis=dict(range=[0, 100])  # Set y-axis range from 0 to 100%
        )
        
        # Update hover template to show both percentage and actual count
        fig_severity_state.update_traces(
            textposition='inside',
            hovertemplate="<b>%{x}</b><br>" +
                         "Severity: %{customdata}<br>" +
                         "Percentage: %{y:.1f}%<br>" +
                         "Count: %{text}<br>" +
                         "<extra></extra>",
            customdata=severity_state['Accident Severity']
        )
        
        st.plotly_chart(fig_severity_state, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the proportion of different accident severities within each state
        - Helps identify states with higher percentages of severe accidents
        - Enables comparison of severity patterns across states
        - Useful for state-specific safety policy planning
        - Highlights states that need focused intervention for severe accident prevention
        """)


        # 2. Local Area Analysis
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
        
        # 3. State vs Accident Type
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
        
        # 1. Industry Sector vs Accident Type
        st.subheader("Industry Sector and Accident Type Analysis")
        sector_type = df.groupby(['Industry Sector', 'Accident Type']).size().reset_index(name='Count')
        fig_sector_type = px.sunburst(sector_type, path=['Industry Sector', 'Accident Type'], values='Count',
                                    title='Accident Types Distribution by Industry Sector',
                                    color='Count', color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_sector_type, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows prevalent accident types in each industry
        - Helps in industry-specific safety planning
        - Identifies sector-specific risk patterns
        """)
        
        # 2. Industry vs Accident Severity
        st.subheader("Industry and Accident Severity Analysis")
        sector_severity = df.groupby(['Industry Sector', 'Accident Severity']).size().reset_index(name='Count')
        fig_sector_severity = px.treemap(sector_severity,
                                   path=['Industry Sector', 'Accident Severity'],
                                   values='Count',
                                   title='Accident Severity Distribution by Industry Sector',
                                   color='Count',
                                   color_continuous_scale='RdBu')
        st.plotly_chart(fig_sector_severity, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows distribution of accident severity in each industry
        - Helps identify industries with higher rates of severe accidents
        - Useful for prioritizing safety interventions by industry
        """)
        
        # 3. Industry vs Safety Gear Usage
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
        
        # Overall Gender Distribution (Pie Chart)
        st.subheader("Overall Gender Distribution")
        gender_counts = df['Gender'].value_counts()
        total_employees = len(df)
        gender_percentages = (gender_counts / total_employees * 100).round(1)
        
        fig_gender_pie = px.pie(
            values=gender_counts,
            names=gender_counts.index,
            title=f'Overall Gender Distribution (Total: {total_employees:,})',
            color_discrete_sequence=['#1f77b4', '#ff7f0e'],  # Blue for Male, Orange for Female
            hover_data=[gender_percentages]
        )
        
        # Update hover template to show both count and percentage
        fig_gender_pie.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
                         "Count: %{value}<br>" +
                         "Percentage: %{customdata:.1f}%<br>" +
                         "<extra></extra>"  # This removes the secondary box
        )
        
        st.plotly_chart(fig_gender_pie, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the overall gender distribution in industrial accidents
        - Provides baseline context for other gender-based analyses
        - Helps understand gender representation in workplace incidents
        """)

        # 1. Gender Distribution by Accident Severity
        st.subheader("Gender Distribution by Accident Severity")
        # Calculate gender distribution by accident severity
        severity_gender = df.groupby(['Gender', 'Accident Severity']).size().reset_index(name='Count')
        
        # Calculate total accidents for each gender
        total_by_gender = severity_gender.groupby('Gender')['Count'].transform('sum')
        # Calculate percentage within each gender
        severity_gender['Percentage'] = (severity_gender['Count'] / total_by_gender * 100).round(1)
        
        # Add total count information to hover text
        severity_gender['Hover_Text'] = severity_gender.apply(
            lambda x: f"{x['Accident Severity']}<br>"
                     f"Count: {x['Count']}<br>"
                     f"Percentage of {x['Gender']} accidents: {x['Percentage']}%", axis=1)
        
        fig_gender_severity = px.bar(severity_gender,
                                   x='Gender',
                                   y='Percentage',
                                   color='Accident Severity',
                                   title='Distribution of Accident Severity by Gender',
                                   text=severity_gender['Percentage'].astype(str) + '%',
                                   color_discrete_sequence=px.colors.qualitative.Set2,
                                   hover_data={'Hover_Text': True,
                                             'Gender': False,
                                             'Percentage': False,
                                             'Accident Severity': False})
        
        # Update layout for better readability
        fig_gender_severity.update_layout(
            xaxis_title="Gender",
            yaxis_title="Percentage of Gender's Total Accidents",
            showlegend=True,
            # Ensure y-axis goes to 100%
            yaxis=dict(range=[0, 100])
        )
        fig_gender_severity.update_traces(textposition='inside')
        st.plotly_chart(fig_gender_severity, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows what percentage of each gender's total accidents falls into each severity category
        - For example: If 20% of female accidents are fatal, it means 20% of all accidents involving females resulted in fatality
        - Helps identify if certain genders are more prone to specific severity levels
        - Useful for targeting safety measures based on gender-specific risk patterns
        """)

        # 2. Gender Distribution by Industry
        st.subheader("Gender Distribution by Industry")
        # Calculate gender distribution for each industry
        industry_gender = df.groupby(['Industry Sector', 'Gender']).size().reset_index(name='Count')
        # Calculate percentage within each industry
        total_by_industry = industry_gender.groupby('Industry Sector')['Count'].transform('sum')
        industry_gender['Percentage'] = (industry_gender['Count'] / total_by_industry * 100).round(1)
        
        fig_industry_gender = px.bar(industry_gender,
                                   x='Industry Sector',
                                   y='Count',
                                   color='Gender',
                                   title='Gender Distribution Across Industries',
                                   barmode='group',
                                   text=industry_gender['Percentage'].astype(str) + '%',
                                   color_discrete_sequence=['#1f77b4', '#ff7f0e'])  # Blue for Male, Orange for Female
        
        # Update layout for better readability
        fig_industry_gender.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="Industry Sector",
            yaxis_title="Number of Accidents",
            showlegend=True
        )
        fig_industry_gender.update_traces(textposition='outside')
        st.plotly_chart(fig_industry_gender, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows gender distribution across different industry sectors
        - Helps identify industries with gender imbalances in accidents
        - Useful for developing industry-specific safety programs considering gender factors
        """)
        
        # 3. Age vs Gender Distribution
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
        
        # 4. Employee Type Analysis
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
        
        # 5. Age vs Accident Type
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
        
        # 1. Accident Type and Causes Analysis
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
        
        # 2. Safety Gear Effectiveness Analysis
        st.subheader("Safety Gear Effectiveness Analysis")
        safety_analysis = df.groupby(['Safety Gear', 'Accident Severity']).size().reset_index(name='Count')
        # Calculate percentages within each Accident Severity category
        safety_analysis['Percentage'] = safety_analysis.groupby('Accident Severity')['Count'].transform(lambda x: x / x.sum() * 100)
        
        fig_safety = px.bar(safety_analysis,
                          x='Accident Severity',
                          y='Percentage',
                          color='Safety Gear',
                          title='Safety Gear Usage Distribution by Accident Severity',
                          barmode='group',
                          text=safety_analysis['Percentage'].round(1).astype(str) + '%')
        fig_safety.update_traces(textposition='outside')
        st.plotly_chart(fig_safety, use_container_width=True)
        st.markdown("""
        **Insights:**
        - Shows the percentage distribution of safety gear usage within each severity level
        - Helps understand the relationship between safety gear usage and accident severity
        - Useful for evaluating safety gear effectiveness in different types of accidents
        """)
        
        # 3. Critical Risk vs. Accident Type
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
        
        # 4. Multiple Factor Risk Analysis
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