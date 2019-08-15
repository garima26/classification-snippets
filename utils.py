#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import datetime as dt
import pycountry
import pandas as pd
import numpy as np

countries = {}
for country in pycountry.countries:
    countries[country.name] = country.alpha_2
    
#Feature engineering functions
def target_fill(col):
    if pd.isnull(col):
        return 0
    return 1


def ip_country(col):
    try:
        match = IPWhois(col).lookup_whois()
        match = match["nets"][0]['country']
    except:
        match = ""
    return match


def attempt_no(col):
    return col[-1]


def days_to_departure(row):
    return abs(pd.to_datetime(row.DepartureDate) - pd.to_datetime(row.timestamp)).days


def vacation_length(row):
    return abs(pd.to_datetime(row.DepartureDate) - pd.to_datetime(row.EndDate)).days
    
def country_ip_flight_match_score(row):
    global countries
    booker = countries.get(row['BookerCountry_Name'])
    origin = countries.get(row['OriginCountryName'])
    dest = countries.get(row['DestinationCountryName'])
    #   ip=row['ip_country']
    score = 0
    #   if (booker==ip and ip==origin) or (booker==ip and ip==dest):
    if (booker == origin) or (booker == dest):
        score += 1
    return score


def one_way_distance(row):
    if row['OneWayOrReturn'] == "One Way":
        try:
            dist = mpu.haversine_distance((row['OriginLatitude'], row['OriginLongitude']),
                                          (row['DestinationLatitude'], row['DestinationLongitude']))
        except:
            dist = -9999
    else:
        dist = 9999
    return dist


def cities_in_itinerary(col):
    return len(col.split("-"))


def email_real_check(row):
    score = 0
    if row['customer_name'] is not None and row['email_id'] is not None:
        l = len(row['customer_name'].astype('str').split(' '))
        score = jellyfish.jaro_distance(row['email_id'].astype('str').lower(),
                                        row['customer_name'].astype('str').lower())

        try:
            if row['dob_month'] in row['customer_name']:
                score += 0.5
            if row['dob_year'] in row['customer_name']:
                score += 0.5
            if row['dob_day'] in row['customer_name']:
                score += 0.5
            if row['customer_name'].astype('str').split(' ')[0] in row['email_id']:
                score += 0.7
            if row['customer_name'].astype('str').split(' ')[l - 1] in row['email_id']:
                score += 0.7
        except:
            pass
    return score


def cabinclass(col):
    if col.split('|')[0].startswith('Economy'):
        clas = 'Economy'
    elif col.split('|')[0].startswith('PremiumEconomy'):
        clas = 'PremiumEconomy'
    elif col.split('|')[0].startswith('Business'):
        clas = 'Business'
    elif col.split('|')[0].startswith('First'):
        clas = 'First'
    else:
        clas = 'Unknown'
    return clas


now = dt.datetime.now()


def get_age(col):
    return now.year - pd.to_datetime(col).year


def booker_is_travel_agency(col):
    if 'travel' in col.lower():
        return True
    else:
        return False


def booking_daytime(col):
    if 11 < col <= 5:
        return '4'
    elif 5 < col <= 9:
        return '3'
    elif 9 < col <= 17:
        return '2'
    else:
        return 1


def booker_age_bracket(col):
    if 18 <= col <= 25:
        return 1
    elif 25 < col <= 40:
        return 2
    elif 40 < col <= 60:
        return 3
    elif col > 60:
        return 4
    else:
        return 5
    
def jaro_similarity(s1, s2):
    
    if s1=='Unknown' or s2=='Unknown':
        return 0
    
    else: 
        len_s1, len_s2 = len(s1), len(s2)

        # The upper bound of the distanc for being a matched character.
        match_bound = np.floor(max(len(s1), len(s2)) / 2) - 1

        # Initialize the counts for matches and transpositions.
        matches = 0  # no.of matched characters in s1 and s2
        transpositions = 0  # no. transpositions between s1 and s2

        # Iterate through sequences, check for matches and compute transpositions.
        for ch1 in s1:  # Iterate through each character.
            if ch1 in s2:  # Check whether the
                pos1 = s1.index(ch1)
                pos2 = s2.index(ch1)
                if abs(pos1 - pos2) <= match_bound:
                    matches += 1
                    if pos1 != pos2:
                        transpositions += 1

        if matches == 0:
            return 0
        else:
            return 1 / 3 * (matches / len_s1 +
                            matches / len_s2 +
                            (matches - transpositions // 2) / matches
                            )
    

def email_real_check2(custname, emailid, dob_year, dob_month, dob_day, score):
    score=score
    
    if custname is None or emailid is None or dob_month is None:
        score=0
        
    elif custname=='Unknown' or emailid=='Unknown':
        score=0
        
    else:
        l=len(custname.split(' '))
        if dob_month in custname:
            score+=0.5
        if dob_year in custname:
            score+=0.5
        if dob_day in custname:
            score+=0.5
        if custname.split(' ')[0] in emailid:
            score+=0.7
        if custname.split(' ')[l-1] in emailid:
            score+=0.7
    return score  

def stratify_sampling(df, tot_out_rows, strat_col):
    rowspercol=round(tot_out_rows/df[strat_col].nunique())
    a=pd.DataFrame()
    
    for strata in range(0,df[strat_col].nunique()):
        print(strata)
        a=a.append(df[df[strat_col]==strata].sample(rowspercol))
        print (a.shape)
    return a.sample(tot_out_rows)

def encode_circular(col, sin_cos, cardinality):
    """Encodes number to circular given the corresponding cardinality.

    Parameters
    ----------
    col : array_like
        Column to be changed

    sin_cos : string
        Sin or cosine tranformation

    cardinality : int
        Cardinality of column (e.g. 24 for hours, 7 for a weekday etc.)

    Returns
    -------
        Transformed array

    """

    if sin_cos == "sin":
        return np.sin(2 * np.pi * col / cardinality)
    if sin_cos == "cos":
        return np.cos(2 * np.pi * col / cardinality)
    
    