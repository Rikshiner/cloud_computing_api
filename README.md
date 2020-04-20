# Cloud Computing API Coursework

Rest API project in Python using Flask to connect with the Studio Ghibli API

# Introduction

This Restful API was created in Flask to utilise data around Studio Ghibli films using data held within a Cassandra Database (Film data) and using an external API for further functionality (Character Data) to allow external users to access this information efficiently using API requests. Further information on the external API can be found at https://ghibliapi.herokuapp.com/.

# Setup

This API is run through an Ubuntu AWS instance where 2 docker containers run the Cassandra Database, to store the data, run the actual API written in Python.

The Cassandra Database stores a CSV file (Saved in Repository as ghibli_films.csv) that holds basic information about past Ghibli films. In order for my API to access this you must create a container with the Database setup and available to connect to by the API.

The full set of commands used to do this are listed in the cassandra commands file in the repository which is also commented to show the relevant steps. A shortened version of this is that we create a cassandra image within docker and populate it with our table by creating a Keyspace and Table before copying in our data.

Once this is done we can then create a second container using the final 2 commands to build a docker image using the information within my DockerFile (This includes the programming language used, the directories to work from, the information to copy into this, the requirements to download and finally the command to run the API itself). This also uses the requirements.txt to inform the Docker build what packages must be installed and it runs the app.py file. All of these can be found and are commented in the repository for further details.

Once this has been run the API is online alongside the Cassandra container and the API can be used with the functionality listed below at the URL of your AWS instance.

# Functionality

The API has several features depending on the request and the URL used.

Internally there are 4 main requests that can be used at "AWS_URL/ghibli", these are GET, POST, PUT and DELETE:

1) GET provides information around films of a certain year and allows users to search according to this by using "AWS_URL/Ghibli/<year>". Once requested the API will be able to contact the cassandra database and pull relevant information for the year, including the titles of any films as well as their current Rotten Tomatoes score, displaying these to the user
  
2) POST allows the user to create new data to be stored within the cassandra database such as an upcoming film title and it's future release data were it to be announced. It allows users to make a simple POST request with a json format and it will inform the user if this is successful. It also has the ability to detect if the information being sent does not fit the format, is missing the title or if it has already been added and informs the user.

3) PUT offers similar functionality to POST in that it can add new information a user sends in a JSON format but also allows the user to update already held data if for instance a film is pushed back and the release date changes. This presents issues around errors and therefore the function can detect if the information provided is already there (With no new information) or if none of the information is held and it must all be added as a new entry. It can also see if there is some data already held but some different data is also provided and can update the entry accordingly, telling the user if any of these requests has been completed.

4) DELTE is the final internal functinality and allows the user to delete entries for instance if a film is cancelled and must therefore be removed. It is also able to manage errors if it is not sent in a JSON format or is missing key information, as with the others, and can also tell if no entry is present so cannot be deleted to avoid confusion with the user as to whether the data is still held. It will also notify a user if the deletion is sucessful.

Externally I call the Studio Ghibli API for additional fuinctionality around Characters, this can be done at the "AWS_URL/characters" URL to search for information around Characters within Studio Ghibli films. It has only a GET functionality as I cannot edit an external API's data:

1) My external GET request provides information around characters that appear in Studio Ghibli films including their name, age and gender. This can be done by searching the characters name at the "AWS_URL/characters/<name>" URL which sends a request to the external Studion Ghibli API and recieves an object back with the relevant data. This data is then made formatted into a JSON before being displayed to the user. Again if this is sucessful the user will recieve notice of this but if the character is not found the user is also alerted.
  
This covers all the information around the goals of the API, it's basic setup and functionality. The files containing or pertaining to the code are also commented to show what each function does. 

Note: The data has not been commented  as it simply shows the column headers and the data itself which is self explanatory. The DockerFile and requirements files also have basic comments but are covered more in the Readme as they are quite short whilst the Cassandra commands and app.py contain step by step comments to describe the process.

Thank you for reading
