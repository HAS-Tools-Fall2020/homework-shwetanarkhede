# Homework Assignment # 14 (Week 14)
## Name: Shweta Narkhede
#### Submission date: Nov, 28th, 2020
___
## **Assignment Questions**
___
1. **What is the paper or project you picked? Include a title, a link the the paper and a 1-2 sentence summary of what its about.**

-  **Title:** *Development of the Community Water Model (CWatM v1.04) – a high-resolution hydrological model for global and regional assessment of integrated water resources management* 
- This paper can be found [here](https://gmd.copernicus.org/articles/13/3267/2020/#section8).   
- **Summary:** 
This paper presents a new large scale hydrological and water resources model named as Community Water Model (CWatM) which can simulate hydrology at different resolutions globally and regionally at daily time steps. This model includes general surface and groundwater hydrological processes but also takes into account human activities, such as water use and reservoir regulation, by calculating water demands, water use, and return flows. Reservoirs and lakes are included in the model scheme.This paper aims to build a community learning environment which is able to freely use an open-source hydrological model and flexible coupling possibilities to other sectoral models, such as energy and agriculture.

2. **What codes and/or data are associated with this paper? Provide any link to the codes and datasets and a 1-2 sentence summary of what was included with the paper (i.e. was it a github repo? A python package?A database? Where was it stored and how?)**

- All the codes and data details associated with this paper are given in the freely accessible github repository named [CWatM](https://github.com/CWatM/CWatM). 
- The data is provided in netCDF format and the codes are in python 3 programming language.
- Although the documnentaion on gitbub repo is very succint, they have provided a link in the readme file for [detailed documentation](https://cwatm.iiasa.ac.at/).  
- This document provides very detailed explaination of each component of model and how it is developed.
- A repo contained a folder with multiple python scripts which looked like a seperate script for each component of the model.
- The data was called in usig .xml script, I was unablt to figure out where it was stored.

3. **Summarize your experience trying to understand the repo: Was their readme helpful? How was their organization? What about documentation within the code itself?**

**Summarize your experience trying to work with their repo: What happened? Where you successful? Why or why not?**

- The readme file in the repo only gave a little information on what is this model is about which is already included in the paper. The information about the repo, structure, instructions to run the codes are not given in the readme file. 
- Having number of python scripts and no readme file for instructions to work with this repo, left me clueless for where to start from. More elaborate readme would have been appreciated.
- Another link provided in the repo for detailed documentation gave information on set up and packages required. Even after following all given instructions, I could not get 'GDAL' package installed to my environment (I created new environment for this, even from base it was showing conflicts), so I could not go ahead and run the model. 

**Summarize your experience working with the data associated with this research. Could you access the data? Where was it? Did it have a DOI? What format was it in?**

- The input data was in the form of netCDF files and some Geotiff or PCRaster maps as mentioned in the documentation. But I was unable to figure out (it wasn't clear from repo/documentation) the source of data. 

**Did this experience teach you anything about your own repo or projects? Things you might start or stop doing?**

- I liked the way they created seperate .py script for each component of model, seperate script of importing data, functions and then bringing all of them together to form a model. 
- The scripts did not have sufficient comments to help user understand the script, so it was very difficult to connect the dots with lots of assumptions. 
- Overall, script looked incomplete and poorly commented, so it was very difficult to follow.
_ I would like to start practice creating sepearte file for model components like importing data, functions, output, plots so the main script would be short and very easy to follow. 