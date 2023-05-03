'''
Use Universal Sentence Encoder to embed extracted strings.

'''

from absl import logging
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import seaborn as sns
import seaborn.objects as so
import json

import umap
import umap.plot

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)
print ("module %s loaded" % module_url)
def embed(input):
  return model(input)


# load raw data 
raw_data_path = "./raw_data" # check wiki_crawl.py

# load 
with open(raw_data_path, 'r') as fp:
    raw_data = json.load(fp)

embed_data_path = './embed_data'

# print list of protocols
protocols = raw_data['protocol']
print(protocols)

# get embeddings
raw_data['embedding']=[]
for ii in range(len(protocols)):
    embedding = embed([raw_data['description'][ii]])
    raw_data['embedding'].append(embedding.numpy().squeeze())
    print('generated vector embeddding for ' + protocols[ii])

# make a dataframe
pd_df = pd.DataFrame.from_dict(raw_data)

# save it 
pd_df.to_pickle(embed_data_path + '/embed')
###################################################################

# load it
pd_df = pd.read_pickle(embed_data_path + '/embed')


# perform umap 
np_array = pd_df['embedding'].to_numpy()

np_array = np.concatenate(np_array)
np_array = np_array.reshape((len( pd_df['embedding']), 512))

# test
np.allclose(pd_df['embedding'][0], np_array[0,:])


embedding = umap.UMAP(n_neighbors = 5, metric='cosine').fit_transform(np_array)
mapper = umap.UMAP(n_neighbors = 5, metric='cosine').fit(np_array)
umap.plot.points(mapper)


# seaborn scatter plot
plot_df = pd.DataFrame()
plot_df['Embed1']=embedding[:,0]
plot_df['Embed2']=embedding[:,1]
plot_df['name']=protocols

so.Plot(plot_df, x="Embed1", y="Embed2", text='name').layout(size=(10,10)).add(so.Dot()).add(so.Text({'fontweight':'bold'}, fontsize=15, alpha=0.5)) # text annotations get overlapped with each other.


# try it with plotly 
import plotly.express as px

fig = px.scatter(plot_df, x="Embed1", y="Embed2", text='name')
fig.update_traces(textposition='top center', title_text = 'Semantic embedding of DeFi protocols')
fig.update_layout(
    height=800
)
fig.show()
fig.write_html('./ploty.html')