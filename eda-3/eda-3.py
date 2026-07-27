import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

country_population = pd.read_csv(r"C:\Users\aleks\Downloads\country_population\country_population.csv", sep=';')

print(country_population)

country_population[country_population["country"] == "Italy"]