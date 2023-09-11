import pandas as pd

# Load the FORMSrating.csv
df = pd.read_csv('data/FORMSratings.csv', encoding='unicode_escape', sep=';')
# select columns (ID and all columns starting with "[obraz ]")

df = df.loc[:, df.columns.str.startswith('[obraz ') | df.columns.str.startswith('ID')]
df = df.melt(id_vars=['ID'], var_name='image', value_name='rating')
# convert the ID column to string
df['ID'] = df['ID'].astype(str)
# extract the part between quotes from the folloqwing string in the image column [obraz "Landscapes_009_h"] 
df['image'] = df['image'].str.extract(r'\[obraz "(.*)"\]')
df['image'] = df['image'].str.replace('.jpg', '')

# read all files in the data/stm folder
import glob
import os

# get all files in the data/stm folder
files = glob.glob('data/stm/*.stm')

# create a list of dataframes
dfs = dict()
df_stm = pd.DataFrame()

# iterate over the files
for file in files:
    filename = os.path.basename(file)
    # get the filename without the extension
    filename = os.path.splitext(filename)[0]
    # remove "person_" from the filename
    filename = filename.replace('person_', '')
    # read the file separator is empty space
    df_temp = pd.read_table(file, header=None, sep='\t')
    # set column names
    df_temp.columns = ["time", "image"]
    df_temp['ID'] = filename
    dfs[filename] = df_temp
    # bind rows to the df_stm dataframe
    df_stm = pd.concat([df_stm, df_temp], ignore_index=True)

df_stm = df_stm.loc[~df_stm["image"].isin(["nothing", "kriz"]), :]
df_stm['image'] = df_stm['image'].str.replace('.jpg', '')
df_stm['image'].value_counts()

df_merged = df_stm.merge(df, on=['ID', 'image'], how='left')
df_merged = df_merged.dropna(subset=['rating'])
df_merged["rating"].value_counts(dropna=False)
# reorder columns
df_merged = df_merged[['ID', 'image', 'rating', 'time']]
df_merged.to_csv('data/image_evaluation.csv', index=False)

# IDS in the FORMSrating.csv that are not in the stm files
ids_stm_missing = df['ID'].loc[~df['ID'].isin(df_stm['ID'].unique())].unique()
# print the ids
print(ids_stm_missing)

ids_forms_missing = df_stm['ID'].loc[~df_stm['ID'].isin(df['ID'].unique())].unique()
print(ids_forms_missing)