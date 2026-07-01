import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sber_data = pd.read_csv(r"C:\Users\aleks\Downloads\sber_data.zip")
sber_data.head()

print(sber_data.tail())
##количество строк 
num_rows = len(sber_data)
print(num_rows)
##количество районов
num_regions = sber_data['sub_area'].nunique()
print(num_regions)
##макс цена 
max_price = sber_data['price_doc'].max()
print(max_price)  
##уровень бе
plt.figure(figsize=(10, 6))
sber_data.boxplot(column='price_doc', by='ecology')
plt.xlabel('Уровень экологии (ecology)')
plt.ylabel('Цена квартиры (price_doc)')
plt.title('Цена квартир в зависимости от экологии района')
plt.suptitle('')  # Убрать автоматический заголовок
plt.show()

avg_prices = sber_data.groupby('ecology')['price_doc'].mean()
least_valued = avg_prices.idxmin()  # Уровень с наименьшей средней цены

print(f"Уровень экологии, который ценится меньше всего: {least_valued}")
print(f"Средняя цена для этого уровня: {avg_prices[least_valued]}")
##