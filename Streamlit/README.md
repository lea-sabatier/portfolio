# Readme - Script Streamlit Project 
### Overview

This folder contains the code to generate an analytical report on the Brazilian company Olist using Streamlit. For your information, it is written in French. 

The report has been split into several tabs: context, customer service, partners, finance, recommendations and bibliography.  
The structure of the code is organized in such a way as to make it easy to interchange elements within tabs, or to add tabs and elements. 

### Streamlit App Structure

In the "tabs" folder, each tab of the streamlit application is represented by a separate file (.py). 

The "recommendations" and "bibliography" files contain exclusively markdown code.
For the "Customer service", "Partners" and "Finance" files, a function has been created for each graphic. In addition, another function called "tab" has been created, enabling the various graphic functions to be called up and positioned as required, either in rows or columns, within the application.

From here, a main file was created. It is used to call up the previous files in the order of our choice, in order to partition them into tabs within the streamlit application.

### Tabs
- **Context Tab**  
  Provides information and insights into the Brazilian market, with a particular focus on e-commerce.

- **Customer service Tab**  
  Analysis of customer satisfaction using data on orders (product categories, delivery times, dates), scores and comments.
  
- **Partners Tab**  
  Analysis of partners (here, sellers) using data on number of sellers, delivery, sales volume, number of photos published per product.
  
- **Finance Tab**  
  Presents financial analysis: sales, average basket, potential cost of reputation and rates of cancelled and unavailable orders. 
  
- **Recommendations Tab**  
  All recommendations reformulated following analysis.
  
- **Bibliography**  
  Link to web articles cited and/or used in the analysis.

### Deployment of the Streamlit App
In order to publish the application online, we need 2 files. The first file is the python script. The second file is a text file (requirements.txt) containing all the versions of the libraries used in the script. 
Then we need to put these 2 files in the same folder in a GitHub repository. 
