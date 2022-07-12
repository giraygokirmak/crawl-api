import os
import json
import time
from urllib.parse import quote_plus
from datetime import datetime
import pandas as pd
import numpy_financial as npf
import pymongo

class Engine:

    def __init__(self):
        
        self.mongourl = os.environ['mongourl']
        username = quote_plus(os.environ['username'])
        password = quote_plus(os.environ['password'])
        uri = 'mongodb+srv://' + username + ':' + password + '@' + self.mongourl + '/?retryWrites=true&w=majority'
        self.client = pymongo.MongoClient(uri)
        self.db = self.client['crawler-db']
            
        print(time.ctime(),'. Engine Initialized') 
        
    def read_rates(self,collection):
        result_data = self.db[collection].find().sort('date',pymongo.DESCENDING).limit(1)[0]['data']
        return result_data

    def calculate_loan(self,amount,maturity):
        loan_data = self.read_rates('loan-collection')
        loan_data_df = pd.DataFrame(loan_data)
        loan_data_df = loan_data_df[amount<=loan_data_df['max_amount']]

        for bank in loan_data_df['bank'].unique():
            tmpDF = loan_data_df[(loan_data_df['bank']==bank) &
                                 (loan_data_df['maturity']==12)][-1:].copy()
            tmpDF['amount_range_limit']=tmpDF['max_amount']
            loan_data_df = pd.concat([loan_data_df,tmpDF],ignore_index=True)

        loan_data_df = loan_data_df[(loan_data_df['maturity']==maturity) &
                     (loan_data_df['amount_range_limit']<= amount)].groupby(['bank']).apply(lambda group: group.loc[group['amount_range_limit'] == group['amount_range_limit'].max()]).reset_index(level=-1, drop=True)

        for idx,row in loan_data_df.iterrows():
            monthly_payment = round(1-npf.pmt(rate=(row['interest_rate']/100)*1.25,nper=maturity, pv=amount),2)
            total_fee = round(amount*row['fee_pct']/100,2)
            loan_data_df.loc[idx,'monthly_payment'] = monthly_payment
            loan_data_df.loc[idx,'total_fee'] = total_fee
            loan_data_df.loc[idx,'total_cost'] = monthly_payment*maturity+total_fee

        if loan_data_df.shape[0]>0:
            loan_data_df = loan_data_df.sort_values(by=['total_cost']).reset_index(drop=True)

        return loan_data_df   
    
    def calculate_interests(self,amount,maturity):
        deposit_data = self.read_rates('deposit-collection')
        
        all_options = []
        for short_name in deposit_data.keys():
            deposit_df = pd.DataFrame(deposit_data[short_name])
            
            selected_maturity = None
            if deposit_df.shape[0]>0:
                max_amount = deposit_df['AnaPara'].max()
                for col in deposit_df.columns:
                    if 'AnaPara' not in col:
                        deposit_df[col] = deposit_df[col].astype(float)

                deposit_df = deposit_df[deposit_df['AnaPara']>=amount]   
                deposit_df = deposit_df[deposit_df['AnaPara']==deposit_df['AnaPara'].min()]

                for item in range(1,len(deposit_df.columns)):
                    col = deposit_df.columns[item]
                    col_min_max = col.split('-')
                    if len(col_min_max)>1:
                        min_mat = int(col_min_max[0])
                        max_mat = int(col_min_max[1])
                        if selected_maturity:
                            continue    
                        elif (min_mat <= maturity <= max_mat):
                            ir = deposit_df[(deposit_df[col]>0)&(deposit_df['AnaPara']>=amount)][col]
                            if ir.shape[0]>0 and ir.values[0]>0:
                                selected_maturity = col

                if selected_maturity in deposit_df.columns:
                    deposit_df = deposit_df[deposit_df[selected_maturity]>0]
                    if deposit_df.shape[0]>0:
                        tmpDF = pd.DataFrame({'bank': short_name, 'interest_rate':deposit_df[selected_maturity].values[0]},index=[0]) 
                        if not tmpDF.empty and max_amount>amount:
                            all_options.append(tmpDF)
                            
        if len(all_options)>0:
            all_options = pd.concat(all_options,ignore_index=True)
            return all_options.sort_values(by=['interest_rate'],ascending=[False])
        else:
            return pd.DataFrame()

              