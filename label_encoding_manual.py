#!/usr/bin/env python
# coding: utf-8

# # Boolean to Int

# In[4]:


all_cat_cols=['affiliate','channelcode','trans_currency','nonmor']

already_binned=['weekend_booking','OrderDateBrandTime_Month']

# Boolean to Int
boolean_cols=list(df.select_dtypes(include=bool).columns)
df[boolean_cols]=df[boolean_cols].astype(int)


# # Label encoding

# In[6]:


#Which columns to encode
label_col_list=[]
for col in all_cat_cols:  
  if col not in already_binned and col not in boolean_cols:    
    if df[col].nunique()<10:       
      label_col_list.append(col)
      
#Encoding
label_en_dict={col: {cat: n for n, cat in enumerate(df[col].astype('category').cat.categories)} 
               for col in label_col_list}

label_en_dict_reverse={col: {n: cat for n, cat in enumerate(df[col].astype('category').cat.categories)} 
               for col in label_col_list}

df.replace(label_en_dict,inplace=True)
df.head()

