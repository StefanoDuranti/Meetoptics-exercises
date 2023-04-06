# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
from bs4 import BeautifulSoup
import json 
import re

website1 = 'https://www.optosigma.com/eu_en/fused-silica-plano-convex-lenses-uncoated-SLSQ-P.html'
cont_web1 = requests.get(website1)

soup1 = BeautifulSoup(cont_web1.text, 'lxml')

# find all the <span class="sku-cell"> elements on the page
sku_cells = soup1.find_all('span', {'class': 'sku-cell'})

#find all grouped elements in the page
group_elements1 = soup1.find_all('tr',{'class',"grouped-item"})

# create the dictionary
dict_optosigma = {}

#find all the parameters listed for the lenses
labels1 = group_elements1[0].find_all('th', {'class': 'col label'})
specs1 = []
for label in labels1:
    # convert them into a list of strings
    specs1.append(label.text.strip())

# this parameter is not always displayed
if 'Availability' in specs1:
    specs1.remove('Availability')

# for each lens
for element in group_elements1:
    # find the sku number
    sku_number = element.find('span', {'class': 'sku-cell'}).text.strip()
    # which becomes the main key of the dictionary
    dict_optosigma[sku_number]={}
    # for each of the specs
    # element.find('td', {'data-th': spec}) gives the value of the spec
    for spec in specs1:
        dict_optosigma[sku_number][spec]=element.find('td', {'data-th': spec}).text.strip()

#save to a dictionary
with open("optosigma.json", "w", encoding='utf8') as outfile:
    json.dump(dict_optosigma, outfile, ensure_ascii=False)
    
#%%
#now for thorlabs

website2 = 'https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=3279'
cont_web2 = requests.get(website2)

soup2 = BeautifulSoup(cont_web2.text, 'lxml')

# extract all the tables from the page
group_elements2 = soup2.find_all('div', {'class': 'row SubGroupDescription'})

# extract the labels
labels2 = group_elements2[0].find_all('th')

specs2 = []
for label in labels2:
    # convert them into a list of strings
    specs2.append(label.text.strip())

# removing 'ReferenceDrawing' from these labels
specs2.remove('ReferenceDrawing')
# removing 'Item #a' as well
specs2.remove('Item #a')

# creating the dictionary
dict_thorlabs = {}

for element2 in group_elements2:
    #for each table
    # first find the lenses tables
    # they are the only tables whose td tags have the align attribute with a value of left
    left_aligned_tables = element2.find_all('tr', {'align': 'left'})
    skus=[]
    for table in left_aligned_tables:
        first_cell = table.find('td') # the sku numbers always have the td tag
        if first_cell is not None and first_cell.text[:2] == 'LA': #they need to contain a lens code
            skus.append(first_cell) # then this is a sku number

    # now the number of lenses listed
    num_lenses = len(skus)
    # now the total number of fields (parameters)
    list_field_lenses = element2.find_all('td', {'align': 'center'})
    # discard the fields with images (they have empty text)
    for indx in list_field_lenses:
        if indx.text=='':
            list_field_lenses.remove(indx)
    #now the number of identifiers
    num_fields = (len(list_field_lenses))//num_lenses

    # cycle over the number of lenses
    for sku in skus:
        # creating the main keys of the dictionary
        dict_thorlabs[sku.text]={}
        # filling them with the specs and using the labels defined in specs2
        for j in range(skus.index(sku)*num_fields,skus.index(sku)*num_fields+num_fields):
            dict_thorlabs[sku.text][specs2[j%num_fields]]=list_field_lenses[j].text

#save to a dictionary
with open("thorlabs.json", "w", encoding='utf8') as outfile:
    json.dump(dict_thorlabs, outfile, ensure_ascii=False)

#%%
# finally merge the two dictionaries
# relevant parameters (common to both):
# focal length, diameter, radius of curvature, center thickness, edge thickness, 
# coating (not included in Thorlabs)

optosigma_lenses = dict_optosigma.keys()
thorlabs_lenses = dict_thorlabs.keys()
optosigma_params = list(dict_optosigma[list(optosigma_lenses)[0]].keys())
thorlabs_params = list(dict_thorlabs[list(thorlabs_lenses)[0]].keys())

#the strings are general and predict the existence of "center" or "centre" and "coating", "coated" and "coat"
strings_to_search = ['foc', 'diameter', 'radius', 'cent\w* thickness', 'edge thickness', r'coat\w*']
new_labels = ['Focal Length (mm)', 'Diameter (mm)', 'Radius of curvature (mm)', 'Center Thickness (mm)', 'Edge Thickness (mm)', 'Coating']
# to homogenize all the parameters, inches will be converted to mm when found

optosigma_keys_tomerge = []
thorlabs_keys_tomerge = []

# select all the strings in the list of strings matching the string_to_search
for string in strings_to_search:
    pattern = re.compile(string, re.IGNORECASE)
    if list(filter(pattern.match, optosigma_params)):
        optosigma_keys_tomerge.append(list(filter(pattern.match, optosigma_params))[0])
    if list(filter(pattern.match, thorlabs_params)):
        thorlabs_keys_tomerge.append(list(filter(pattern.match, thorlabs_params))[0])

# the coating information is not contained in Thorlabs data
thorlabs_keys_tomerge.append('Coating')

# now select the OptoSigma data and clean them
merged_dict = {}
for opt_lens in optosigma_lenses:
    merged_dict['OptoSigma/'+str(opt_lens)]={}
    # the OptoSigma entries contain "mm" in most cases
    # re.findall(r'\d+\.\d+|\d+', line) filters only decimal numbers
    for new_key_opto in new_labels:
        new_index = optosigma_keys_tomerge[new_labels.index(new_key_opto)]
        if new_key_opto!=optosigma_keys_tomerge[-1]: # if the parameter is not the coating
            merged_dict['OptoSigma/'+str(opt_lens)][new_key_opto]=float(re.findall(r'\d+\.\d+|\d+',dict_optosigma[str(opt_lens)][new_index])[0])
        else: # if it is the coating, don't extract the digits
            merged_dict['OptoSigma/'+str(opt_lens)][new_key_opto]=dict_optosigma[str(opt_lens)][new_index]

# now Thorlabs (data are already clean except for inches)
# inches will be converted to mm when found
# this is the function to do it

def inches_convert_to_mm(string):
    # the usual pattern for inches is either things like 1/2" (fractions) or 2.5" (decimals)
    string = string[:-1]
    result = eval(string)
    return float(result*25.4)


for thor_lens in thorlabs_lenses:
    merged_dict['Thorlabs/'+str(thor_lens)]={}
    for new_key_thor in new_labels:
        new_index = thorlabs_keys_tomerge[new_labels.index(new_key_thor)]
        if new_key_thor!=thorlabs_keys_tomerge[-1]: # if the parameter is not the coating
            # if the parameter is the diameter and it contains a value in inches
            if new_index=='Diameter(mm)' and dict_thorlabs[str(thor_lens)][new_index][-1]=='"':
                # then convert the value to mm
                merged_dict['Thorlabs/'+str(thor_lens)][new_key_thor]=inches_convert_to_mm(dict_thorlabs[str(thor_lens)][new_index])
            else:
                # otherwise it is already in mm
                merged_dict['Thorlabs/'+str(thor_lens)][new_key_thor]=float(dict_thorlabs[str(thor_lens)][new_index])
        else: # if it is the coating, I set it manually to the specs on the webpage (the coating is always the same)
            merged_dict['Thorlabs/'+str(thor_lens)][new_key_thor]='AR Coating: 350 - 700 nm'

#save to a dictionary
with open("merged_dictionary.json", "w", encoding='utf8') as outfile:
    json.dump(merged_dict, outfile, ensure_ascii=False)