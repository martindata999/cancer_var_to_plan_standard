import streamlit as st
import pandas as pd
from p_v_a_scatterplots import plot_chart_1, get_dataframe

# Load data_metrics DataFrame
data_metrics = pd.read_excel("data/planvactual_testextract.xlsx", sheet_name="metrics")

data = get_dataframe()

# Extract unique planning_ref values
planning_refs = data_metrics["measure_name"].unique()

st.title("South East Planning Analysis")

chosen_metric = st.selectbox(
    "Choose metric",
    planning_refs
)

# Display the first chart
st.header("Chart 1")
plot_chart_1(chosen_metric)

# Filter data_plan by chosen_metric
filtered_data_plan = data[data["measure_name"] == chosen_metric]

# Display the filtered DataFrame if the checkbox is selected
if st.checkbox('Show dataframe'):
    st.write(filtered_data_plan)