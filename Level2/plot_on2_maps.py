# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 09:44:20 2026

@author: Luiz
"""
import base as b 

df = b.load('on2')

df =  df.groupby([pd.Grouper(freq="D"), "site"])["mean"].mean().unstack("site")

df.plot() 