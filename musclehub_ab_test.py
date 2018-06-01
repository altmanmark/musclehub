#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 07:03:42 2018

@author: mark
"""
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
#Left join the other tabels based on first_name, last_name, and email
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
import pandas as pd
from matplotlib import pyplot as plt

#Add column to new dataset
#A if fitness_test_date is not None and B if fitness_test_date is None
df['ab_test_group'] = df.fitness_test_date.apply(lambda x: \
  'B' if x == 'None' else 'A')
print(df.head(10))