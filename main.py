import streamlit as st
import pandas as pd
from p_v_a_scatterplots import plot_chart_1  # Import your chart functions

# Load data_metrics DataFrame
data_metrics = pd.read_excel("data/planvactual_testextract.xlsx", sheet_name="metrics")

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