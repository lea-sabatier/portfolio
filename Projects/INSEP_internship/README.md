# End-of-study project at INSEP (The French National Institute for Sport, Expertise and Performance)

## Aim of the project 
This project involved the statistical analysis of power and cadence data from 2 instruments: an ergometer (Lode Excalibur) and instrumented pedals (Favero Assioma) in order to measure the validity and reliability of the pedals.

Experienced cyclists came to the laboratory 9 times to carry out tests. During these tests, data was collected at different power levels and cadences for further analysis.

## Project progress

### Interpolation of ergometer data 
The output files for the experimental protocol were in Excel format (ergometer and pedals included). 
Firstly, the ergometer data had to be interpolated to the second, as the pedals collected data per second. This work can be seen in the script entitled "interpolation_ergometer".

### Evaluation of pedal reliability
For pedal reliability, outliers were removed from each file (+-3 standard deviations from the mean) and the mean and standard deviation of each participant's power and cadence were calculated. 

This work can be seen in the scripts entitled "reliability_various_tests" and "reliability_constant_tests". We have 2 scripts because the 'reliability_constant_tests' script refers to tests carried out at a constant cadence and power for each participant, whereas the 'reliability_various_tests' script refers to tests carried out at various cadences and powers. 

These scripts each return an Excel file containing all the participants, with a sheet for the power results and a sheet for the cadence results. This file was then used to measure the coefficient of variation of each power meter. 

### Evaluation of pedal validity
In summary, descriptive statistics were used to determine the validity of the pedals. The mean, standard deviation, bias, precision and confidence interval (Bland-Altman parameters) were calculated. Inferential statistics were also calculated, using the Shapiro-Wilk test to determine whether the data followed the normal distribution, then the Student or Wilcoxon test to measure potential differences between the two instruments, and Cohen's D if necessary. This work can be seen in the "validity" script. 

This script returns an Excel file for each participant this time. 
Each file contains 3 sheets: 
- power results for constant power tests
- power results for tests at various power levels
- cadence results.
  
### Automation
All the scripts described above have been automated so that the code has to be run once for all the participants. 

### Final graphics
The "graphics" script contains all the graphs presented in my report. Boxplots and scatter plots were used to illustrate Pearson's correlation coefficient, as well as Bland-Altman diagrams.

### Function script
A script named "function" contains all the functions used in the various scripts. Each function has a "docstring" to explain how it works. 

![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?style=for-the-badge&logo=scipy&logoColor=%white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)
