# FALL2021 SI 507 Final Project

## Introduction
This project aims to build a website for users to see the details of a movie input, details of a star input and learn the filmography that two input stars worked together. The ratings detials are shown in graphs. A bipartite graph are drawn for user to visualize the filmography that two stars worked together. Several basic programming techniques are adopted in the project, which includes accessing data efficiently with caching via scraping and web API, storing and presenting data with graphs, using base64, matplotlib and Flask for data visualization on html page, etc.

## Data Sources
(1) The details of rating are crawled from the page "https://www.imdb.com/title/" + <movie_id> + "/ratings". The URL direct to the details of ratings page for the indicated movie. The data is crawled and processed with BeautifulSoup and graphs are drawn with the data.

(2) The other details of stars and movies are retrieved from RapidAPI. (https://rapidapi.com/apidojo/api/imdb8/)

## Run the Program
### Step 1: Apply an API Key for RapidAPI
(1) Go to "https://rapidapi.com/apidojo/api/imdb8/pricing" and sign up for the website and subscibe the api to get a key. 

(2) Go to the python file "secret.py" and add the code: 
'x-rapidapi-key': ''your-key''
to the header

### Step 2: Install packages
```
$ pip install -r requirements.txt --user
```  

### Step 3: Run program.py  
```  
$ python main.py
```  
### Step 4: Open "http://127.0.0.1:5000/ " in a browser
