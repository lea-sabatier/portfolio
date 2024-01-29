# Pre-processing job categories in Python

```python
# Importing data
import pandas as pd
df = pd.read_csv('C:/Users/leasabatier/Downloads/salaries.csv')
df.head()
```
```python
# Dataset information
df.info()
```
```python
# Delete columns 'salary' and 'salary_currency'
df.drop(['salary', 'salary_currency'], axis='columns', inplace=True)
```
```python
# The 5 most represented jobs
df['job_title'].value_counts().head(5)
```
```python
# List of unique jobs
liste_jobs = df['job_title'].unique().tolist()
print(liste_jobs)
```

```python
# Count the number of occurrences of each value in the 'job_title' column
occurrences = df['job_title'].value_counts()
# Filter results to include only those with more than 10 occurrences
noms_plus_de_10_occurrences = occurrences[occurrences > 10].index.tolist()
# Display the list
print(noms_plus_de_10_occurrences)
```

### Categorize jobs into 5 main categories for better display in Power Bi

```python
#"Manual" categorization of jobs that occur more than 10 times in the dataset into 5 categories
data_scientist_group = ['Data Scientist', 'Research Scientist', 'Applied Scientist', 'Machine Learning Scientist',
                        'Data Science Consultant', 'Decision Scientist', 'Data Science', 'Applied Machine Learning Scientist',
                       'Data Science Engineer']

data_engineer_group = ['Data Engineer', 'Research Engineer', 'Computer Vision Engineer', 'ETL Developer', 
                'Data Operations Engineer', 'Data Operations Engineer', 'Data Infrastructure Engineer', 'Data Modeler', 
                       'Data Strategist']

data_analyst_group = ['Data Analyst', 'Analytics Engineer', 'Business Intelligence Engineer', 'BI Developer', 'Research Analyst',
                     'BI Analyst', 'Business Intelligence Developer', 'BI Data Analyst']

IA_group = ['AI Engineer', 'AI Scientist', 'AI Architect', 'AI Programmer','Machine Learning Engineer','ML Engineer', 
           'Machine Learning Infrastructure Engineer', 'Machine Learning Researcher','Machine Learning Software Engineer',
            'Deep Learning Engineer','MLOps Engineer','NLP Engineer', 'AI Developer']

manager_data_group = ['Data Manager', 'Data Science Manager', 'Data Analytics Manager', 'Head of Data', 
                      'Director of Data Science','Data Science Lead', 'Data Lead','Head of Data Science', 'Data Product Manager']

def categorie_job(job):
    if job in data_scientist_group:
        return 'Data Scientist'
    elif job in data_engineer_group:
        return 'Data Engineer'
    elif job in data_analyst_group:
        return 'Data Analyst'
    elif job in IA_group:
        return 'AI'
    elif job in manager_data_group:
        return 'Manager Data'
    else:
        return 'Autres'
    
df['job_category'] = df['job_title'].apply(categorie_job)   
df
```

```python
# Save in csv format
df.to_csv('C:/Users/leasa/Documents/salaries_traiter.csv', index=False)
```

![Photo 1](https://github.com/lea-sabatier/portfolio/blob/main/images/PowerBI_1.png)
