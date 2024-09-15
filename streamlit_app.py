# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 17:47:40 2024

@author: rakumar
"""

import streamlit as st
import pyodbc
from datetime import datetime
import pandas as pd

class ItemDatabase:
    def __init__(self):
        # Connect to the SQL Server database
        self.conn = pyodbc.connect('DRIVER={SQL SERVER};SERVER=TAR-HOSQL02Dev;DATABASE=DWH;')
        self.cursor = self.conn.cursor()

    def get_items(self, col_name, value, specific_columns, start_date=None, end_date=None):
        result = []
        columns_str = ', '.join(specific_columns)
        query = f"SELECT {columns_str} FROM Targray_All_Price WHERE {col_name}=?"
        
        # Add date filter if provided
        if start_date and end_date:
            query += " AND Contract_Month BETWEEN ? AND ?"
            self.cursor.execute(query, (value, start_date, end_date))
        else:
            self.cursor.execute(query, (value,))
        
        for i in self.cursor.fetchall():
            try:
                # Assuming Contract_Month is in the format '2027-01-01'
                contract_month_obj = datetime.strptime(i[2], '%Y-%m-%d')  # Parse 'YYYY-MM-DD'
                contract_month = contract_month_obj.strftime('%Y-%b-%d')  # Format to '2027-Jan-01'
            except ValueError:
                contract_month = i[2]
            
            item_dict = {
                'Commodity_Code': i[0],
                'Price': float(i[1]),  # Ensure price is a float
                'Contract_Month': contract_month
            }
            result.append(item_dict)
        
        return result

# Create an instance of the ItemDatabase
db = ItemDatabase()

# Streamlit app
def main():
    st.title("Item Database Query")

    col_name = st.text_input("Column Name", "")
    value = st.text_input("Value", "")
    specific_columns = st.text_input("Specific Columns (comma-separated)", "")
    
    start_date = st.date_input("Start Date", value=None)
    end_date = st.date_input("End Date", value=None)
    
    if st.button("Get Items"):
        if not col_name or not value or not specific_columns:
            st.error("Missing parameters. Please fill in all required fields.")
        else:
            specific_columns_list = [col.strip() for col in specific_columns.split(',')]
            
            try:
                # Try converting value to integer if possible
                value = int(value)
            except ValueError:
                pass  # Keep value as string if it's not an integer
            
            result = db.get_items(col_name, value, specific_columns_list, start_date, end_date)
            
            if result:
                df = pd.DataFrame(result)
                st.write("Results:")
                st.dataframe(df)
            else:
                st.write("No results found.")

if __name__ == "__main__":
    main()
