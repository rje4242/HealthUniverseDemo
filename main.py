import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st

# st.title("Welcome to Health Universe!")
# st.write("This is a sample application.")

# Create a simple Matplotlib plot
fig, ax = plt.subplots()
x = [1, 2, 3, 4, 5]
y = [10, 20, 15, 30, 25]
ax.plot(x, y)

# Display the Matplotlib plot using Streamlit
st.pyplot(fig)
