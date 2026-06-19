import pandas as pd

df = pd.read_csv(r"C:\Users\aleks\Downloads\churn.zip")

#9.1. Соотношение ушедших и лояльных
import seaborn as sns
import matplotlib.pyplot as plt

df = df.drop(columns=['RowNumber'])          # если ещё не удалили
ax = sns.countplot(x='Exited', data=df)

total = len(df)
for p in ax.patches:
    count = p.get_height()
    ax.annotate(f'{count} ({count/total:.1%})',
                (p.get_x() + p.get_width()/2, count),
                ha='center', va='bottom')
plt.show()

#9.2. Распределение баланса при Balance > 2500
subset = df[df['Balance'] > 2500]
sns.histplot(subset['Balance'], bins=30, kde=True)
plt.show()

#9.3. Баланс в разрезе оттока (Exited)
sns.boxplot(x='Exited', y='Balance', data=df)
plt.show()

#9.4. Возраст и отток: выбросы и сегменты
sns.boxplot(x='Exited', y='Age', data=df)
plt.show()

#9.5. Взаимосвязь CreditScore и EstimatedSalary с расцветкой по Exited
sns.scatterplot(data=df,
                x='CreditScore',
                y='EstimatedSalary',
                hue='Exited',
                alpha=0.5)
plt.show()

#9.6. Кто чаще уходит: мужчины или женщины
churn_by_gender = df.groupby('Gender')['Exited'].mean().reset_index()
sns.barplot(x='Gender', y='Exited', data=churn_by_gender)
plt.show()

#9.7. Отток и количество продуктов (NumOfProducts)
churn_by_prod = df.groupby('NumOfProducts')['Exited'].mean().reset_index()
sns.barplot(x='NumOfProducts', y='Exited', data=churn_by_prod)
plt.show()

#9.8. Статус активного клиента и отток (IsActiveMember)
churn_by_active = df.groupby('IsActiveMember')['Exited'].mean().reset_index()
sns.barplot(x='IsActiveMember', y='Exited', data=churn_by_active)
plt.show()

#9.9. В какой стране доля ушедших больше (Geography + карта)
churn_by_geo = df.groupby('Geography')['Exited'].mean().reset_index()

#9.10. CreditScore → CreditScoreCat и тепловая карта по CreditScoreCat × Tenure
def get_credit_score_cat(credit_score):
    if credit_score >= 300 and credit_score < 500:
        return "Very_Poor"
    elif credit_score >= 500 and credit_score < 601:
        return "Poor"
    elif credit_score >= 601 and credit_score < 661:
        return "Fair"
    elif credit_score >= 661 and credit_score < 781:
        return "Good"
    elif credit_score >= 781 and credit_score < 851:
        return "Excellent"
    elif credit_score >= 851:
        return "Top"
    elif credit_score < 300:
        return "Deep"

df['CreditScoreCat'] = df['CreditScore'].apply(get_credit_score_cat)

pivot = df.pivot_table(
    index='CreditScoreCat',
    columns='Tenure',
    values='Exited',
    aggfunc='mean'
)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.heatmap(pivot, annot=True, fmt='.2f', cmap='Reds')
plt.ylabel('CreditScoreCat')
plt.xlabel('Tenure')
plt.show()