import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# Function to process the log file
def process_log_file(file):
    lines = file.readlines()
    
    pmid_list = []
    year_list = []
    doi_status_list = []

    pmid_pattern = re.compile(r'PMID:\s(\d+),')
    year_pattern = re.compile(r'Year:\s(\d{4}),')
    
    paragraph = []
    processed_pmids = set()

    for line in lines:
        line = line.decode('utf-8').strip()
        paragraph.append(line)
        
        if "cached results for key" in line or "No DOI, skipping" in line:
            paragraph_text = " ".join(paragraph)
            
            pmid_match = pmid_pattern.search(paragraph_text)
            year_match = year_pattern.search(paragraph_text)
            
            if pmid_match and year_match:
                current_pmid = pmid_match.group(1)
                current_year = year_match.group(1)
                
                if current_pmid in processed_pmids:
                    paragraph = []
                    continue
                
                if "No DOI, skipping" in paragraph_text:
                    doi_status = 'No DOI'
                else:
                    doi_status = 'Has DOI'
                    
                pmid_list.append(current_pmid)
                year_list.append(current_year)
                doi_status_list.append(doi_status)
                processed_pmids.add(current_pmid)
            
            # Reset for next paragraph
            paragraph = []

    data = {'PMID': pmid_list, 'Year': year_list, 'DOI_Status': doi_status_list}
    df = pd.DataFrame(data)
    
    return df

# Streamlit UI
st.title("Log File DOI Analysis")

uploaded_file = st.file_uploader("Upload a log file", type="log")

if uploaded_file is not None:
    df_extracted = process_log_file(uploaded_file)

    # Display the extracted DataFrame
    st.write("Extracted Log Data", df_extracted)
    
    # Calculate the percentage of papers without a DOI
    doi_counts = df_extracted['DOI_Status'].value_counts()
    percentage_no_doi = (doi_counts['No DOI'] / doi_counts.sum()) * 100 if 'No DOI' in doi_counts else 0
    
    st.write("DOI Status Counts", doi_counts)
    st.write("Percentage of papers without a DOI:", percentage_no_doi)
    
    # Analyze the distribution of DOI statuses over the years
    doi_year_counts = df_extracted.groupby(['Year', 'DOI_Status']).size().unstack().fillna(0)
    
    # Plot the distribution of papers with and without a DOI over different years
    plt.figure(figsize=(14, 7))
    doi_year_counts.plot(kind='bar', stacked=True)
    plt.title('Distribution of Papers with and without a DOI over Years')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.legend(title='DOI Status')
    plt.tight_layout()
    
    st.pyplot(plt)

