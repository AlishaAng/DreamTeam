# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 18:37:16 2020

@author: sheri
"""

from Database.kinase_functions import *
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from pprint import pprint
import csv 
import pandas as pd 
import re
import numpy as np
import math
from scipy.stats import norm
from bokeh.models import Span
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.plotting import figure, ColumnDataSource, show, output_file
from bokeh.models import HoverTool, WheelZoomTool, PanTool, BoxZoomTool, ResetTool, TapTool, SaveTool


def data_analysis(filename, p_val, CV, Sub):
    
    Sub=float(Sub)
    CV=float(CV)
 
    #df_input_original = pd.read_csv(filename, sep='\t')
    df_input_original = pd.read_csv("instance/Data_Upload/"+ filename,  sep='\t')
   
    input_original_subset = df_input_original.iloc[:, 0:7]
   
    col_number =  input_original_subset.shape[1]
    
    if col_number == 5:
        input_original_subset["control_cv"] = 0
        input_original_subset["condition_cv"] = 0  
    
        
    df_cols=["Substrate", "control_mean", "inhibitor_mean", "fold_change", "p_value", "ctrlCV", "treatCV" ]

    input_original_subset.columns=df_cols
    input_original_subset.iloc[:, 0]=input_original_subset.iloc[:, 0].astype(str)

    input_original_subset=(input_original_subset[~input_original_subset['Substrate'].str.contains("None")] ) #drop rows with "None"



    met_regex1 = r"\([M]\d+\)" #Use Regex to find "(M and any number of digits)"


    input_original_subset=(input_original_subset[~input_original_subset.Substrate.str.contains(met_regex1)].copy()) #d1: rows with (Mddd) removed....copy() to remove conflict
    #Make columns 2-7 type float instead of string

    input_original_subset['ctrlCV'] = input_original_subset['ctrlCV'].replace(np.nan, 3)
    input_original_subset["treatCV"]=input_original_subset["treatCV"].replace(np.nan, 3)

    input_original_subset.iloc[:, 1:7] = input_original_subset.iloc[:, 1:7].astype(float)

    #Need to separate the phosphosite from the substrate in the first column into 2 separate columns
    input_original_subset[['Substrate','Phosphosite']] = input_original_subset.Substrate.str.split('\(|\)', expand=True).iloc[:,[0,1]]

    
    input_original_subset=input_original_subset.dropna(axis=1, how="all")
   
    #Take -log10 of the corrected p-value.
    uncorrected_p_values=input_original_subset.iloc[ :,4].astype(np.float64)
    log10_corrected_pvalue = (-np.log10(uncorrected_p_values))

    #Append -log10(P-values) to a new column in data frame.
    input_original_subset["-Log10 Corrected P-Value"]=log10_corrected_pvalue
    NegLog10Kinase=input_original_subset
    
    NegLog10Kinase.loc[:, "fold_change"].replace([np.inf, -np.inf], 0, inplace=True)
    log2FC=np.log2(NegLog10Kinase.iloc[:, 3])

    NegLog10Kinase["Log2 Fold Change"]=log2FC
    
    log2FCKinase = NegLog10Kinase
   
    log2FCKinase.loc[:, "Log2 Fold Change"].replace([np.inf, -np.inf], 0, inplace=True)
    final_substrate=log2FCKinase
   
    # Replace nan with 0.
    log2FCKinase.loc[:, "Log2 Fold Change"] =log2FCKinase.loc[:,"Log2 Fold Change"].fillna(0)
   
    Final_substrate=log2FCKinase
    Sub_phosp_list=[]
    for i, j, k in zip(log2FCKinase['Substrate'], log2FCKinase['Phosphosite'],range(len(log2FCKinase))):
        Sub_phosp_list.append([])
        Sub_phosp_list[k].append(i)
        Sub_phosp_list[k].append(j)
        
    KinaseList=[]
    substrates={x: None for x in get_all_substrates_complete()}
    for i in Sub_phosp_list:
        Sub = i[0]
        Pho = i[1]
        if Sub in substrates:
            KinaseList.append(get_kinase_substrate_phosphosite(Sub, Pho))
        else:
            KinaseList.append([])
            
    input_original_subset['Kinase']=KinaseList

    df_final = pd.concat([input_original_subset, input_original_subset['Kinase'].apply(pd.Series)], axis = 1).drop('Kinase', axis = 1)
    df_final1=df_final.drop(['substrate', 'phosphosite'], axis=1)

    df_final2=df_final1.dropna()
    df_final2=df_final2.explode('kinase')
    df_final3=df_final2.dropna(subset = ["kinase"])
    
    df_final3= df_final3[(df_final3['ctrlCV'] <= CV) & (df_final3['treatCV'] <= CV)]  
    
    mS = df_final3.groupby('kinase')['Log2 Fold Change'].mean()
    mP = df_final3['Log2 Fold Change'].mean()
    delta=df_final3['Log2 Fold Change'].std()

    m=[]
    Kinase_phosphosite=df_final3.groupby('kinase')['Phosphosite']
    for key, item in Kinase_phosphosite:
        m.append(len(item))

    Z_Scores=[]    
    for i, j in zip(mS, m):
        Z_Scores.append(((i-mP)*math.sqrt(j))/delta)

    p_means=[]
    for i in Z_Scores:
        p_means.append(norm.sf(abs(i)))
    
    calculations_dict={'mS': mS, 'mP':mP, 'm':m, 'Delta':delta, 'Z_Scores':Z_Scores,"P_value":p_means}

    calculations_df=pd.DataFrame(calculations_dict)
    calculations_df=calculations_df.reset_index(level=['kinase'])
    final_substrate=final_substrate.drop(['Kinase'], axis=1)
    
    return (calculations_df, final_substrate ,df_final3) 

def VolcanoPlot_Sub(final_substrate, p_val, FC, CV):
    
    FC=float(FC)
    FC_N = -(float(FC))
    PV=-np.log10(float(p_val))

    final_substrate.loc[(final_substrate['Log2 Fold Change'] > FC) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'color' ] = "Green"  # upregulated
    final_substrate.loc[(final_substrate['Log2 Fold Change'] < FC_N) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'color' ] = "Red"   # downregulated
    final_substrate['color'].fillna('grey', inplace=True)


    final_substrate.loc[(final_substrate['Log2 Fold Change'] > FC) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'regulation' ] = "More abundant in treatment"  # upregulated
    final_substrate.loc[(final_substrate['Log2 Fold Change'] < FC_N) & (final_substrate['-Log10 Corrected P-Value'] > PV), 'regulation' ] = "Less abundant in treatment"   # downregulated
    final_substrate['regulation'].fillna('No change', inplace=True)

    category = 'Substrate'

    category_items = final_substrate[category].unique()
    title="Summary of Proteins in Sample"

    source = ColumnDataSource(final_substrate)

    hover = HoverTool(tooltips=[
                                ('Substrate', '@Substrate'),
                                ('Phosphosite', '@Phosphosite'),
                                ('Fold_change', '@{Log2 Fold Change}'),
                                ('p_value', '@{-Log10 Corrected P-Value}')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
 
    p = figure(tools=tools,title=title, plot_width=700,plot_height=400,toolbar_location='right',
           toolbar_sticky=False)
   
    p.circle(x = 'Log2 Fold Change', y = '-Log10 Corrected P-Value',source=source,size=10,color='color', legend='regulation')

    p_sig = Span(location=PV,dimension='width', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_over=Span(location=FC,dimension='height', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_under=Span(location=FC_N,dimension='height', line_color='black',line_dash='dashed', line_width=3)

    p.add_layout(p_sig)   
    p.add_layout(fold_sig_over)   
    p.add_layout(fold_sig_under)   
    
    p.xaxis.axis_label = "Log2 Fold Change"
    p.yaxis.axis_label = "-Log10 Corrected P-Value"
        
    html=file_html(p, CDN, "Volcano Plot of Substrates" )

    return html


def VolcanoPlot(df_final3, p_val, FC, CV):
   # calculations_df, final_substrate, df_final3=data_analysis(filename, CV)
    FC=float(FC)
    FC_N=-(float(FC))
    PV=-np.log10(float(p_val))

    df_final3.loc[(df_final3['Log2 Fold Change'] > FC) & (df_final3['-Log10 Corrected P-Value'] > PV), 'color' ] = "Green"  # upregulated
    df_final3.loc[(df_final3['Log2 Fold Change'] < FC_N) & (df_final3['-Log10 Corrected P-Value'] > PV), 'color' ] = "Red"   # downregulated
    df_final3['color'].fillna('grey', inplace=True)

    df_final3.loc[(df_final3['Log2 Fold Change'] > FC) & (df_final3['-Log10 Corrected P-Value'] > PV), 'regulation' ] = "Upregulated"  # upregulated
    df_final3.loc[(df_final3['Log2 Fold Change'] < FC_N) & (df_final3['-Log10 Corrected P-Value'] > PV), 'regulation' ] = "Downregulated"   # downregulated
    df_final3['regulation'].fillna('No Change', inplace=True)

    category = 'Substrate'

    category_items =df_final3[category].unique()
    title="Kinase Activity Summary"

    source = ColumnDataSource(df_final3)

    hover = HoverTool(tooltips=[('Kinase','@kinase'),
                                ('Substrate', '@Substrate'),
                                ('Phosphosite', '@Phosphosite'),
                                ('Fold_change', '@{Log2 Fold Change}'),
                                ('p_value', '@{-Log10 Corrected P-Value}')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    
    p = figure(tools=tools,title=title,plot_width=700,plot_height=400,toolbar_location='right',
           toolbar_sticky=False)
   
    p.circle(x = 'Log2 Fold Change', y = '-Log10 Corrected P-Value',source=source,size=10,color='color', legend= 'regulation')
   
    p_sig = Span(location=PV,dimension='width', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_over=Span(location=FC,dimension='height', line_color='black',line_dash='dashed', line_width=3)
    fold_sig_under=Span(location=FC_N,dimension='height', line_color='black',line_dash='dashed', line_width=3)

    p.add_layout(p_sig)   
    p.add_layout(fold_sig_over)   
    p.add_layout(fold_sig_under)  
    
    p.xaxis.axis_label = "Log2 Fold Change"
    p.yaxis.axis_label = "-Log10 Corrected P-Value"
    

    html=file_html(p, CDN, "Volcano Plot of Filtered Kinases" )
    return html

def EnrichmentPlot(calculations_df, p_val, FC, CV, Sub):
 
    
    reduc_calculations_df=calculations_df[calculations_df['m']>= float(Sub)]
    reduc_calculations_df=reduc_calculations_df.sort_values(by='Z_Scores')

    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] < float(p_val)), 'color'] = "Orange"  # significance 0.05# significance 0.01
    reduc_calculations_df.loc[(reduc_calculations_df['P_value'] > float(p_val)), 'color' ] = "Black"

    kinase=reduc_calculations_df['kinase']

    z_score=reduc_calculations_df['Z_Scores']
    source = ColumnDataSource(reduc_calculations_df)

    hover = HoverTool(tooltips=[('Z-Score','@Z_Scores'),
                                ('Number of Substrates', '@m'),
                                ('P-value', '@P_value'),
                                ('Kinase', '@kinase')])

    tools = [hover, WheelZoomTool(), PanTool(), BoxZoomTool(), ResetTool(), SaveTool()]
    p = figure(tools=tools, y_range=kinase, x_range=((z_score.min()-5), (z_score.max()+5)), plot_width=600, plot_height=800, toolbar_location=None,
           title="Kinase Substrate Enrichment",)
    p.hbar(y="kinase", left=0, right='Z_Scores', height=0.3, color= 'color', source=source)

    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = "Z Score"
    p.yaxis.axis_label = "Kinase"
    p.outline_line_color = None

    html=file_html(p, CDN, "Ratio of Enrichment" )
    return html

def df2_html(calculations_df):
    df_final_html=calculations_df.to_html()
    return df_final_html