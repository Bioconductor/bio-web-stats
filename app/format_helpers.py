
import pandas as pd

def dataframe_to_string_list(df):
    headers = list(df.columns)
    header_string = "\t".join(headers)
    rows = [header_string]
    for _, row in df.iterrows():
        row_string = "\t".join(map(str, row))
        rows.append(row_string)
    return rows

def dataframe_to_text_tab(df: pd.DataFrame, df2: pd.DataFrame) -> [str]:

    # Extract Year and Month
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.strftime('%b')

    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    all_years = df['Year'].unique()
    all_packages = df['Package'].unique()

    # Create reference dataframe with all possible combinations
    ref_df = pd.DataFrame(index=pd.MultiIndex.from_product([all_packages, all_years, all_months], names=['Package', 'Year', 'Month'])).reset_index()

    # Merge with original dataframe
    merged_df = pd.merge(ref_df, df, on=['Package', 'Year', 'Month'], how='left').fillna(0)


    # Process the second dataframe
    df2['Year'] = df2['date'].dt.year
    df2['Month'] = 'all'

    # Concatenate and sort
    final_df = pd.concat([merged_df, df2], ignore_index=True)
#    final_df.sort_values(by=['Package', 'date'], inplace=True)
    final_df.drop('date', axis=1, inplace=True)

    # Convert to list of strings
    formatted_output = dataframe_to_string_list(final_df)
    return formatted_output




# Sample dataframe for monthly data
data = {
    'Package': ['ABarray'] * 20,
    'date': pd.to_datetime(['2022-11-01', '2022-12-01', '2023-01-01', '2023-02-01', '2023-03-01',
                            '2023-04-01', '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01',
                            '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01', '2024-01-01',
                            '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01', '2024-06-01']),
    'Nb_of_distinct_IPs': [33, 34, 49, 40, 43, 48, 68, 55, 41, 58, 58, 11, 10, 9, 8, 7, 6, 5, 4, 3],
    'Nb_of_downloads': [80, 85, 97, 91, 65, 88, 88, 88, 89, 147, 76, 13, 14, 15, 16, 17, 18, 19, 20, 21]
}
df = pd.DataFrame(data)

# Sample dataframe for yearly data
data2 = {
    'Package': ['ABarray', 'ABarray'],
    'date': pd.to_datetime(['2023-12-31', '2024-12-31']),
    'Nb_of_distinct_IPs': [500, 450],
    'Nb_of_downloads': [1200, 1100]
}
df2 = pd.DataFrame(data2)

result = dataframe_to_text_tab(df, df2)
# Display the output
for line in result:
    print(line)
