#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 19:12:26 2018

@author: olya
"""

import argparse
import copy
import numpy as np
import pandas as pd

def apply_single_cond(df, cond):
    for symbol in ['>=', '<=', '>','<', '=']:
        parts = cond.split(symbol)
        if len(parts)>1:
            attr = parts[0].strip()
            value = parts[1].strip()
            try:
                value = np.float(value)
                if symbol=='>=':
                    df = df[df[attr]>=value]
                elif symbol=='<=':
                    df = df[df[attr]<=value]
                elif symbol=='>':
                    df = df[df[attr]>value]
                elif symbol=='<':
                    df = df[df[attr]<value]
                elif symbol=='=':
                    df = df[df[attr]==value]
                return df
            except:
                try:
                    value = str(value).strip().strip("'").strip('"')
                    if symbol=='>=':
                        df = df[df[attr]>=value]
                    elif symbol=='<=':
                        df = df[df[attr]<=value]
                    elif symbol=='>':
                        df = df[df[attr]>value]
                    elif symbol=='<':
                        df = df[df[attr]<value]
                    elif symbol=='=':
                        df = df[df[attr]==value]
                    return df
                except:
                    return df

def apply_name_cond(df, table_name, cond_str):
    name_split = cond_str.split('.')
    if len(name_split)==1:
        df = apply_single_cond(df, cond_str)
        return df
    if len(name_split)==2:
        cond_name = name_split[0]
        cond = name_split[1]
        if not cond_name.strip()==table_name.strip():
            return df
        df = apply_single_cond(df, cond)
        return df
    else:
        print ("No functionality for it yet")

def upper_by_word(s, l=list()):
    words = [word.strip() for word in s.split(' ')]
    res_words = list()
    for word in words:
        if word.lower() in l:
            word = word.upper();
        res_words.append(word)
    res = ' '.join(res_words)
    return res

class Query():
    def __init__(self, query=''):
        upper_query = upper_by_word(query, ['select', 'from', 'join', 'on', 'where', 'and', 'or', 'not'])
        self.query = upper_query.replace('(','').replace(')','')
        self.tables_paths = list()
        self.tables_names = list()
        self.table_dict = dict()    # dictionary of table_name -> data path
        self.table_attrs = dict()   # dictionary of table_name -> list of attributes needed
        self.general_attrs = list()  # attributes wihtout corresponding table name mentioned
        self.where_query = ''
        self.table_conditions = dict()      # dictionary of table_name -> list of conditions
        self.general_conditions = list()    # list of conditions without corresponding table name mentioned
        self.on_queries = list()
        self.output = pd.DataFrame()
        self.chunk_size = 5000
        self.current_chunk = pd.DataFrame()
        
    def parse(self):
        from_split = self.query.split(' FROM ')
        select_query = from_split[0].replace('SELECT ','')
        select_attrs = [attr.strip() for attr in select_query.strip().split(',')]
        for attr in select_attrs:
            attr_split = attr.strip().split('.')
            if len(attr_split)<2:
                self.general_attrs.append(attr_split[0])
            else:
                key = attr_split[0];
                value_attr = attr_split[1];
                if not key in self.table_attrs:
                    self.table_attrs[key] = list()
                self.table_attrs[key].append(value_attr)
        
        fromwhere_query = from_split[1]
        where_split = fromwhere_query.split(' WHERE ')
        from_join_on_query = where_split[0]
        on_split = from_join_on_query.split(' ON ')
        on_query = ''
        if len(on_split)>1:
            on_query = on_split[1].strip()
        on_query_split = on_query.split(' AND ')
        self.on_queries = [q.strip() for q in on_query_split if len(q.strip())>0]
        from_join_query = on_split[0].strip()
        
        join_query = from_join_query.split(' JOIN ')
        from_tables = [table.strip() for table in join_query]
        
        where_query = ''
        if len(where_split)>1:
            where_query = where_split[1]
            self.where_query = where_query
        for pair_str in from_tables:
            pair = pair_str.split(' ')
            path = pair[0].strip()
            self.tables_paths.append(path)
            name = ''
            if len(pair)>1:
                name = pair[1].strip()
                self.table_dict[name] = path
            self.tables_names.append(name)
                
                
#        print ('\n')
#        print ('select_query: \n', select_query)
#        print ('general attr:\n', self.general_attrs)
#        print ('table attrs:\n', self.table_attrs)
#        print ('tables paths:\n')
#        for i in range(len(self.tables_names)):
#            print (self.tables_names[i], '\t', self.tables_paths[i])
#        print ('table dict:\n', self.table_dict)
#        print ('on_queries:\n', self.on_queries)
#        print ('where query:\n', where_query)
#        print ('\n')
            
    def load_data(self):
        if len(self.tables_paths)==1:
            table_name = self.tables_names[0]
            for df in pd.read_csv(self.tables_paths[0], chunksize=self.chunk_size, iterator=True):
                self.current_chunk = df
                self.process_chunk_single(table_name)
            self.data = df
        elif len(self.tables_paths)==2:
            for merge_cond in self.on_queries:
                print(merge_cond)
                cond_split = [s.strip() for s in merge_cond.split('=')]
                if len(cond_split)<2:
                    print ("Two parts needed in JOIN ON, please fix")
                    return
                name1 = cond_split[0].split('.')[0]
                attr1 = cond_split[0].split('.')[1]
                name2 = cond_split[1].split('.')[0]
                attr2 = cond_split[1].split('.')[1]
                path1 = self.table_dict[name1]
                path2 = self.table_dict[name2]
                print (name1, name2, attr1, attr2, path1, path2)
                for df1 in pd.read_csv(path1, chunksize=self.chunk_size, iterator=True):
                    for df2 in pd.read_csv(path2, chunksize=self.chunk_size, iterator=True):
                        df1_chunk = apply_conditions(df1, name1, self.where_query)
                        df2_chunk = apply_conditions(df2, name2, self.where_query)
                        self.current_chunk = pd.merge(df1_chunk, df2_chunk, left_on=attr1, right_on=attr2, how='inner', copy=False)
                        self.process_chunk([name1, name2])
        else:
            print ("\nFunctionality to work with >= 3 tables is under construction, please check out later")
        
    def optimize(self):
        pass
            
    def process_chunk_single(self, table_name):
#        chunk_output = self.current_chunk
        chunk_output = copy.deepcopy(self.current_chunk)
        final_attrs = list()
        if '*' in self.general_attrs:
            final_attrs = self.current_chunk.columns
        else:
            final_attrs.extend(self.general_attrs)
            if table_name in self.table_attrs:
                final_attrs.extend(self.table_attrs[table_name])
                
        chunk_output = apply_conditions(chunk_output, table_name, self.where_query)
        self.output = pd.concat([self.output, chunk_output[final_attrs]], axis=0)
                
    def process_chunk(self, tables_names=list()):
#        chunk_output = self.current_chunk
        chunk_output = copy.deepcopy(self.current_chunk)
        final_attrs = list()
        if '*' in self.general_attrs:
            final_attrs = self.current_chunk.columns
        else:
            final_attrs.extend(self.general_attrs)
            for table_name in tables_names:
                if table_name in self.table_attrs:
                    final_attrs.extend(self.table_attrs[table_name])
        
        self.output = pd.concat([self.output, chunk_output[final_attrs]], axis=0)
        
def apply_conditions(df, table_name, conditions):
    if conditions.strip()=='':
        return df
    if not ((' OR ' in conditions) or (' AND ' in conditions) or ('NOT ' in conditions)):
        df_res = apply_name_cond(df, table_name, conditions)
        return df_res
    
    
    df_res = pd.DataFrame()

    if ' OR ' in conditions:
        or_split = conditions.split(' OR ')
        for cond in or_split:
            dfi = apply_conditions(df, table_name, cond)
            df_res = pd.concat([df_res, dfi], axis=0)
        df_res = df_res.drop_duplicates()
        return df_res

    elif ' AND ' in conditions:
        and_split = conditions.split(' AND ')
        for cond in and_split:
            dfi = apply_conditions(df, table_name, cond)
            if df_res.empty:
                df_res = copy.deepcopy(dfi)
            else:
                df_res = pd.merge(df_res, dfi, how='inner')
        return df_res
    
    elif 'NOT ' in conditions:
        not_split = conditions.split('NOT ')
        not_conds = [cond.strip() for cond in not_split if len(cond.strip())>0]
        not_cond = not_conds[0]
        dfi = apply_conditions(df, table_name, not_cond)
        merged = pd.merge(df, dfi, how='outer', indicator=True)
        df_res = merged[merged['_merge'] == 'left_only']
        df_res = df_res.drop(columns=['_merge'])
        return df_res
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help='query to process')
    args = parser.parse_args()
    query = args.query
    
    q = Query(query)
    q.parse()
    q.load_data();
#    q.optimize();

#    print ('\nQuery:\n', q.query)
#    print ('\nOutput:\n', q.output.to_string(index=False))
    print ('\n', q.output.to_string(index=False))
    
if __name__ == '__main__':
    main();