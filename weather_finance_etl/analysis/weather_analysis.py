import plotly.express as px

def plot_temperature(df):
    fig = px.bar(df, x="city", y="temp_c", title="Temperature by City")
    return fig