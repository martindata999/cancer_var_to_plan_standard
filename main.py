import streamlit as st
from p_v_a_scatterplots import plot_chart_1  # Import your chart functions

st.title("South East Planning Analysis")

# Display the first chart
st.header("Chart 1")
plot_chart_1()