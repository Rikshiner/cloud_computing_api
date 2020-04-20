#Import relevant files, Flask to build the api with json to deal with file types, requests to make calls to external api, cassandra to call to the cassandra db and cache to cache requests
from flask import Flask, request, jsonify, json
from cassandra.cluster import Cluster
import requests
import requests_cache

#Simple Cache to story the frequently made requests so the API does not need to make requests every time
requests_cache.install_cache('studio_ghibli_cache', backend='sqlite', expire_after=36000)

#Connects to the Cassandra cluster through the contact points(IP address and Port)
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
#Creates the connection through  which requests are made
session = cluster.connect()
#Runs the API app
app = Flask(__name__)

#URL to the external API which adds character details functionality
characters_url = 'https://ghibliapi.herokuapp.com/people?name={name}'

#App route creates initial web page at '/' to welcome people to the API using the definition Hello
@app.route('/')
def hello():
  return('<h1>Welcome to the Studio Ghibli Api, you can search films and characters!</h1>')

#App route at Ghibli followed by a year date (Eg. 2002) creates a Get request to search for films on that date
@app.route('/ghibli/<release_date>', methods = ['GET'])
def date_profile(release_date):
    #As films are stored in Cassandra we connect to the DB through session (see above) and use CQL to retrieve data relating to the date requested
    rd_rows = session.execute( "Select * FROM ghibli.films where release_date = {} ALLOW FILTERING".format(release_date))
    #For the rows of data found I extract the data and 2 options take place, if data is found the release date, title and rotten tomatoes score are given to the user
    for films in rd_rows:
        return('<h1>In {} Studio Ghibli released {} and it recieved a rotten tomatoes score of {}</h1>'.format(release_date,films.title,films.rt_score)), 200
    #If no film is found an not found erorr is given
    return('<h1>That film does not exist!</h1>'), 404

#External API Get request, this time calling characters with the name of whatever character the user choosed
@app.route('/ghibli/characters/<name>', methods = ['GET'])
def character_profile(name):
    #As we are calling external api I use flask requests to call to the URL (listed above) to get the relevant data
    character_response_object = requests.get(characters_url.format(name = name))
    #As response is an object I turn this into a json to make it useable
    character_response_json = character_response_object.json()
    for characters in character_response_json:
        #If request is found name, gender and age are provided to the user for the character, and if not a Not Found error is given
        return('<h1>{} is a character from Studio Ghibli they are {} and they are {} years old</h1>'.format(characters['name'],characters['gender'],characters['age'])), 200
    return('<h1>That character does not exist!</h1>'), 404

#Post request to the cassandra DB to add films to our API database
@app.route('/ghibli/films', methods=['POST'])
def new_films():
    #To ensure good requests if the title (Primary Key) is not given or it is not in a json it will give a Bad Request error
    if not request.json or not 'title' in request.json:
        return jsonify({'error' : 'the new film needs to have a title!'}), 400
    #To ensure titles are not added twice we also search the cassandra DB to see if it is already there using our session connect (Above) and CQL commands to Cassandra
    title_error = session.execute("""Select count(*) FROM ghibli.films where title = '{}'""".format(request.json['title']))
    for titles in title_error:
        titles_count = titles.count
    #We search the data found from this request, if the same film is already added the request will recieve a bad request error
    if titles_count == 1:
        return jsonify({'error' : 'this film already exists!'}), 400
    #If the data is not already held we connect to cassnadra again and insert the new data with a message confirming this. New data in our case is title and release date
    session.execute("""INSERT INTO ghibli.films(title,release_date) VALUES ('{}',{})""".format(request.json['title'],request.json['release_date']))
    return jsonify({'message' : 'created film: {}'.format(request.json['title'])}), 201

#Put request to the cassandra DB to add and update films to our API database
@app.route('/ghibli/films', methods=['PUT'])
def  update_films():
    #To ensure good requests if the title (Primary Key) is not given or it is not in a json it will give a Bad Request error
    if not request.json or not 'title' in request.json:
        return jsonify({'error' : 'the updated film needs to have a title!'}), 400
    #A Put request can both update and put in new data, this search is done to see if the title has already been entered or not
    title_error = session.execute("""Select count(*) FROM ghibli.films where title = '{}'""".format(request.json['title']))
    for titles in title_error:
        titles_count = titles.count
    #A Put request can both update and put in new data, this search is done to see if the title AND information related to that title have already been added
    entered_error = session.execute("""Select count(*) FROM ghibli.films where release_date = {} AND title = '{}' ALLOW FILTERING""".format(request.json['release_date'],request.json['title']))
    for entered in entered_error:
        entered_error_count = entered.count
    #This finds if the title has not been entered previously, if it hasn't then we can simply enter it as a new piece of data (As with POST method)
    if titles_count == 0:
        session.execute("""INSERT INTO ghibli.films(title,release_date) VALUES ('{}',{})""".format(request.json['title'],request.json['release_date']))
        return jsonify({'message' : 'created film: {}'.format(request.json['title'])}), 201
    #This finds if the title has been entered previously but the other data does not match. If it does not it is considered an update and the cassandra DB is updated
    if titles_count == 1 and entered_error_count != 1:
        session.execute("""UPDATE ghibli.films set release_date = {} WHERE title ='{}'""".format(request.json['release_date'],request.json['title']))
        return jsonify({'message' : 'updated film: {}'.format(request.json['title'])}), 200
    #Finally if the title and data are the same there is no need to update and therefore it is flagged as a bad request
    if entered_error_count == 1:
        return jsonify({'error' : 'Data already entered, you must enter new data!'}), 400

#Delete request to the Cassandra DB allowing the user to delete data held by the api
@app.route('/ghibli/films', methods=['DELETE'])
def delete_films():
    #To ensure good requests if the title (Primary Key) is not given or it is not in a json it will give a Bad Request error
    if not request.json or not 'title' in request.json:
        return jsonify({'error' : 'the new film needs to have a title!'}), 400
    #This checks the current data held within the Cassandra DB to see if there is data to be deleted
    title_error = session.execute("""Select count(*) FROM ghibli.films where title = '{}'""".format(request.json['title']))
    for titles in title_error:
        titles_count = titles.count
    #If there are no entries found matching the request a Not Found error is given
    if titles_count == 0:
        return jsonify({'error' : 'No film found called: {}'.format(request.json['title'])}), 404
    #If data is found however, this is then deleted from the cassandra DB using the same methods described above using the CQL commands
    session.execute("""DELETE FROM ghibli.films WHERE title = '{}'""".format(request.json['title']))
    return jsonify({'message' : 'deleted film: {}'.format(request.json['title'])}), 200

#These final lines run the code with the local host at port 80
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
