#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 07:03:42 2018

@author: mark
"""
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
from scipy.stats import chi2_contingency
mpl.rcParams['font.size'] = 18.0

#Import SQLite database from Codecademy and examine the tables
#Tables included are visits, fitness_tests, applications, purchases
from codecademySQL import sql_query

sql_query('''
SELECT *
FROM visits
LIMIT 5
''')

sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')

sql_query('''
SELECT *
FROM applications
LIMIT 5
''')

sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')

#Create giant database from the 4 provided datasets
#Createa  query where we pull data from visits on or after 7-1-17.
#Left join the other tables based on first_name, last_name, and email
df = sql_query('''
SELECT visits.first_name,
       visits.last_name,
       visits.visit_date,
       fitness_tests.fitness_test_date,
       applications.application_date,
       purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.first_name = visits.first_name
    AND fitness_tests.last_name = visits.last_name
    AND fitness_tests.email = visits.email
LEFT JOIN applications
    ON applications.first_name = visits.first_name
    AND applications.last_name = visits.last_name
    AND applications.email = visits.email
LEFT JOIN purchases
    ON purchases.first_name = visits.first_name
    AND purchases.last_name = visits.last_name
    AND purchases.email = visits.email
WHERE visits.visit_date >= '7-1-17'
''')


#Investigate groups A and B

#Add column to new dataset
#Label A if there is a fitness_test_date and B if there is no fitness_test_date
df['ab_test_group'] = df.fitness_test_date.apply(lambda x: \
                                                  'B' if pd.isna(x) else 'A')

#Check the size of the sample sets A and B
ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()

#Create a pie chart of this information
#test_groups = ['Fitness Test', 'No Fitness Test']
plt.figure(figsize=(12,8))
plt.pie(ab_counts.first_name.values, 
        labels=['Fitness Test', 'No Fitness Test'], 
        colors=['#7EDFA0', '#DF7EBD'], 
        autopct='%0.2f%%', 
        labeldistance=1.1, 
        startangle=90)
plt.axis('equal')
plt.title('Test Groups', size=24)
#plt.show()
plt.savefig('Test-Groups_pie-chart.png', transparent=True)


#Who picks up and application?
#Add another column and show how many people filled out and application
df['is_application'] = df.application_date.apply(lambda y: \
                                                 'No Application' if pd.isna(y) else 'Application')

#Count how many from Group A and Group B do or don't pick up an application.
app_counts = df.groupby(['ab_test_group', 'is_application']).first_name.count().reset_index()

#Pivot table so the index is ab_test_group with our columns as is_application
app_pivot = app_counts.pivot(columns = 'is_application',
                             index = 'ab_test_group',
                             values = 'first_name')\
            .reset_index()

#Sum totals of Application and No Application
app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']

#Calculate the percent if applications
app_pivot['Percent with Application'] = app_pivot.Application / app_pivot.Total * 1.0
print(app_pivot)

#Run a Chi2 test to see if percent application is significant (p<0.05)
table = [[250, 2254], [325, 2175]]
chi2, pval_1, dof, expected = chi2_contingency(table)


#Who purchases a membership?
#Add column to determine membership by if there is a purchase date
df['is_member'] = df.purchase_date.apply(lambda z: \
                                                 'Not Member' if pd.isna(z) else 'Member')

#Create a dataframe with only those who picked up an application
just_apps = df[df.is_application == 'Application']

#Group those who picked up an application by membership
member_counts = just_apps.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

member_pivot = member_counts.pivot(columns = 'is_member',
                               index = 'ab_test_group',
                               values = 'first_name')\
               .reset_index()
               
#Sum totals of Member and Not Member. Then calculate the percentage
member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']

member_pivot['Percent Purchase'] = member_pivot.Member / member_pivot.Total * 1.0
print(member_pivot)


#Null hypothesis is that there is no statisitcal difference in someone buying a membership if they peformed a
#fitness test and picked up an application

member_table = [[200, 50], [250, 75]]
chi2, pval_2, dof, expected = chi2_contingency(member_table)
#pval_2 is .43 which means we have to accept our null hypothesis


#Create one more look where we figure out the percentage of All Visitors and 
#if they purchased a membership
final_member_counts = df.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()

final_member_pivot = final_member_counts.pivot(columns = 'is_member',
                               index = 'ab_test_group',
                               values = 'first_name')\
                     .reset_index()

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']

final_member_pivot['Percent Purchase'] = final_member_pivot.Member / final_member_pivot.Total * 1.0
print(final_member_pivot)

final_member_table = [[200, 2304], [250, 2250]]
chi2, pval_3, dof, expected = chi2_contingency(final_member_table)

#Create bar charts to show comparisons between
#Visitors who applied
#Applicants who purchased a membership
#Visitors who purchased a membership

#Percentage of Visitors who applied
plt.figure(figsize=(10,8))
ax = plt.subplot()
plt.bar(range(len(app_pivot)),
        app_pivot['Percent with Application'].values,
        color='#EDA8A8')
ax.set(title='Percentage of Visitors who Applied')
ax.xaxis.set(ticks=range(len(app_pivot)),
             ticklabels=['Fitness Test', 'No Fitness Test'])
ax.yaxis.set(ticks=[0, 0.05, 0.10, 0.15, 0.20],
             ticklabels=['0%', '5%', '10%', '15%', '20%'])
plt.savefig('Percent_Visitors.png', transparent=True)
plt.show()

#Percentage of applicants who purchased a membership
plt.figure(figsize=(10,8))
ax = plt.subplot()
plt.bar(range(len(member_pivot)),
        member_pivot['Percent Purchase'].values,
        color='#A8A8ED')
ax.set(title='Percentage of Applicants who are Members',
       ylim=[0.60, 0.85])
ax.xaxis.set(ticks=range(len(member_pivot)),
             ticklabels=['Member', 'Not Member'])
ax.yaxis.set(ticks=[0.60, 0.65, 0.70, 0.75,  0.80, 0.85],
             ticklabels=['60%', '65%', '70%', '75%', '80%', '85%'])
plt.savefig('Percent_Member_Application.png', transparent=True)
plt.show()

#Percentage of visitors who purchased a membership
plt.figure(figsize=(10,8))
ax = plt.subplot()
plt.bar(range(len(final_member_pivot)),
        final_member_pivot['Percent Purchase'].values,
        color='#A8EDA8')
ax.set(title='Percentage of Visitors who are Members',
       ylim=[0.0, 0.15])
ax.xaxis.set(ticks=range(len(final_member_pivot)),
             ticklabels=['Member', 'Not Member'])
ax.yaxis.set(ticks=[0, 0.05, 0.10, 0.15],
             ticklabels=['0%', '5%', '10%', '15%'])
plt.savefig('Percent_Member_Visitor.png', transparent=True)
plt.show()