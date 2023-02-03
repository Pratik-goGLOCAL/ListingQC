# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 15:05:42 2023

@author: pratik
"""

# Import packages

import pandas as pd
import language_tool_python
import numpy as np
import re
from tqdm import tqdm
from loguru import logger
from fuzzywuzzy import fuzz

# Load Data
special_char = pd.read_csv('Special characters list.csv')['chars']
my_tool = language_tool_python.LanguageTool('en-US')

###########################################################################################################
# Helper Functions
###########################################################################################################
## Sentence Case
def sentence_case(brand_name,title,brand_present_title):
    first_word = title.strip().split(' ')[0]
#     print(brand_name,first_word,brand_present_title)
    if brand_present_title==1:
        if brand_name.strip()[0]==first_word[0]:
            res = 1
        else:
            res = 0
    else:
        if first_word[0].isupper():
            res = 1
        else:
            res = 0
#     print(res)
    return res

###########################################################################################################
## Spell Check
def spellcheck(my_text,my_tool):
    # using the tool
#     logger.info(my_text)  
    # getting the matches  
    my_matches = my_tool.check(my_text)  
#     logger.info(my_matches)
    # defining some variables  
    myMistakes = []  
    myCorrections = []  
    startPositions = []  
    endPositions = []  

    # using the for-loop  
    for rules in my_matches:  
        if len(rules.replacements) > 0:  
#             startPositions.append(rules.offset)  
#             endPositions.append(rules.errorLength + rules.offset)  
            myMistakes.append(my_text[rules.offset : rules.errorLength + rules.offset])  
            myCorrections.append(rules.replacements[0])
    if len(myMistakes)>0:
        return 0
    else:
        return 1
    # return [myMistakes,myCorrections,startPositions,endPositions]
    
###########################################################################################################
## Special Character Check
def special_char_check(x):
    if len(set(special_char[0])) - len(set(special_char[0].tolist())-set(x))>0:
        return 0
    else:
        return 1

###########################################################################################################
## Get complete Title Flag
def get_Title_flag(data):
    ## Brand Name Present
    bn_check = lambda x,y:1 if y.split(' ')[0].strip().lower()==x.strip().lower() else 0
    data['title_brand_present'] = data[['product_brand','product_title']].apply(lambda x:bn_check(x.brand_name,x.title),axis = 1)

    ## Sentence Case
    data['title_sentence_case'] = data[['product_brand','product_title',"title_brand_present"]].apply(lambda x:sentence_case(x.brand_name,x.title,x.title_brand_present),axis = 1)

    ## Spell Check
    data['title_spellcheck'] = data['product_title'].progress_apply(lambda x:spellcheck(x,my_tool))
    data['final_title_check_flag'] = data[['title_brand_present','title_sentence_case','title_spellcheck']].product(axis = 1)
    return data['final_title_check_flag']

###########################################################################################################
## Get complete Description Flag
def get_Description_flag(data):
    ## Special Character Check
    data['description_special_chr_check'] = data['description'].apply(lambda x:special_char_check(x))
    ## Characters Constrained
    data['description_char_constrained_2000'] = data['description'].apply(lambda x:1 if len(x.strip())<=2000 else 0)
    ## Multiline Check
    def multiline_check(x):
        first_str = data['description'][3]
        order = "[+-]?\d+\.\d+"
        first_str = re.sub(order, '', first_str)
        lines = re.split( r'[?.!]',first_str)
        if len(lines)>1:
            return 1
        else:
            return 0
    
    data['description_multiline_check'] = data['description'].apply(lambda x:multiline_check(x))
    ## Spell Check 
    data['description_spellcheck'] = data['description'].progress_apply(lambda x:spellcheck(x,my_tool))
    ## Final Description check Flag
    data['final_description_check_flag'] = data[['description_special_chr_check','description_char_constrained_2000','description_multiline_check','description_spellcheck']].product(axis = 1)

    return data['final_description_check_flag']

###########################################################################################################
## Get complete BulletPoints Flag
def get_BulletPoints_flag(data):
    ## Special Character check
    data['bullets_special_chr_check'] = data['product_bullets'].apply(lambda x:special_char_check(x))
    ## Number of bullet points check (atleast 3 points)
    data['bullets_number_check'] = data['product_bullets'].progress_apply(lambda x:1 if x.count('\n')>=2 else 0)
    ## Bullet Points start with capital letter check
    data['bullets_first_capital_check'] = data['product_bullets'].apply(lambda x: int(''.join([s[0] for s in x.split('\n')]).isupper()) )
    ## Spell Check
    data['bullets_spellcheck'] = data['product_bullets'].progress_apply(lambda x:spellcheck(x,my_tool))
    ## Final Bullet Points check Flag
    data['final_bullet_point_check_flag'] = data[['bullets_special_chr_check','bullets_number_check','bullets_first_capital_check','bullets_spellcheck']].product(axis = 1)

    return data['final_bullet_point_check_flag']

###########################################################################################################
## Get complete Spell Check Flag
def get_sum(lst):
    return sum(lst)

def get_SpellCheck_flag(data):
    data['final_entire_spellcheck'] = data[['title_spellcheck','description_spellcheck','bullets_spellcheck']].product(axis = 1)
    return data['final_entire_spellcheck']

###########################################################################################################
## Get complete Dimension Check Flag
def qc_dim(unit,values):
#     metric = {'meter':['m','meter'],
#     'centimeter':['cm','cms','centimeter'],
#     'millimeter':['mm','millimeter'],
#     'inches':['inch','inches']
#     'litre':['l','lit','litre'],
#     'gram':['g','gm','gram'],
#     'kilogram':['kg','kgms','kilogram']}
#     metric = ['meter','centimeter','millimeter','kilometer','inches','foot']
    metric2 = ['m','cms','mm','km','inches','ft']
    metric_change = [1,0.01,0.001,1000,0.0254,0.0348]
    metric_unit= []
    logger.info('unit for qc {}\nvalue for qc {}'.format(unit,values))
    for u in unit:
        umetric_ratio = []
        for m in metric2:
            umetric_ratio.append(fuzz.ratio(u,m))
        metric_unit.append(metric2[np.array(umetric_ratio).argmax()])
    logger.info('metric_unit {}'.format(metric_unit))
    updated_values = [float(v)*metric_change[metric2.index(i)] for i,v in zip(metric_unit,values)]
    logger.info('updated values {}'.format(updated_values))
    if len(set(metric_unit))>1:
        qc_res = [0,updated_values]
    else:
        qc_res = [1,updated_values]
    
    return qc_res

def format_dim(dim):
    logger.info('initial dim {}'.format(dim))
    dim = dim.replace(' ','').lower()
    dim = dim.replace('x',' ')
    units = []
    for unit in re.finditer("[a-z]+",dim):
        units.append(unit.group())
    values = []
    for val in re.finditer("[0-9]+",dim):
        values.append(val.group())
    logger.info('unit is {} and values are {}'.format(units,values))
    return [units,values]

def check_values(value_list):
    logger.info('value_list for check values {}'.format(value_list))
    value_list = [sorted(l) for l in value_list]
    logger.info('after sort {}'.format(value_list))
    same_val_list = np.array(value_list).T.tolist()
    logger.info('transform for each dim {}'.format(same_val_list))
    res = 1
    for v in same_val_list:
        ratio_list = [v[i]/v[0] for i in range(len(v))]
        logger.info('ratio list for list {} {}'.format(v,ratio_list))
        res*=np.prod([1 if (i<=1.05 and i>=0.95) else 0 for i in ratio_list])
    logger.info('res {}'.format(res))
    return res

def get_dimensions(text):
    iters = re.finditer("(((\d+ ?[a-zA-Z]+ ?)[x,X] ?(\d+ ?[a-zA-Z]+ ?)[x,X] ?(\d+ ?[a-zA-Z]+ ?))|((\d+ ?[a-z]+ ?)[x,X] ?(\d+ ?[a-zA-Z]+ ?)))|(((\d+ ?)[x,X] ?(\d+ ?)[x,X] ?(\d+ ?[a-zA-Z]+))|((\d+ ?)[x,X] ?(\d+ ?[a-zA-Z]+)))",text)
    matched_strings = []
    for i in iters:
        matched_strings.append(i.group())
    logger.info('matched_strings {}'.format(matched_strings))
    if len(matched_strings)==0:
        return [0,0,0]
    same_unit_in_dim = 1
    multi_units_value = []
    for dim in matched_strings:
        units, values = format_dim(dim)
        if len(units)==1:
            units = units*len(values)
        qc_res = qc_dim(units,values)
        same_unit_in_dim*=qc_res[0]
        multi_units_value.append(qc_res[1])
    return [1,same_unit_in_dim,check_values(multi_units_value)]
            
def get_Dimensions_flag(data):
    data['complete_data'] = data['product_title']+data['description']+data['product_bullets']#+
    data['dimensionality_inter_check'] = data['complete_data'].progress_apply(lambda x: get_dimensions(x))
    return data['dimensionality_inter_check']

###########################################################################################################
## Get complete Spell Check Flag
def get_SentenceCase_flag(data):
    data['final_sentence_case_check'] = data['title_sentence_case']
    return data['final_sentence_case_check']

##############################################################################################################
## Get all the flags
def QC_check1(data):
    data['final_title_check_flag'] = get_Title_flag(data.copy())

    data['final_description_check_flag'] = get_Description_flag(data.copy())

    data['final_bullet_point_check_flag'] = get_BulletPoints_flag(data.copy())

    data['final_entire_spellcheck'] = get_SpellCheck_flag(data.copy())

    data['final_dimensionality_check'] = get_Dimensions_flag(data.copy())

    data['final_sentence_case_check'] = get_SentenceCase_flag(data.copy())

    return data