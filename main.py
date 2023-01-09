from fastapi import FastAPI
import json
import requests
#import mysql.connector
import pymysql
import re


api = FastAPI(title="Tracknow API")

'''
[ {
        ● vehicleId
        ● lat
        ● long
        ● timestamp
        ● speed
        ● engineStatus
        ● Location name
        ● Vehicle direction angle
        ● Fuel data
} ]
'''


@api.get("/current_state/")
def current_state(clientid, vehicleids):
    responselist = []
    vehicleids = vehicleids.replace('\"', '')
    vehicleids = vehicleids.replace('"', '')
    vehicleidsList = vehicleids[1:-1].split(",")
    api_hash = "$2y$10$B3j6pYUWdewxAiiXJA4KW.Q6j8I7J5UmUWG0EtT9SWz79xKAFnaF."
    jsonobj = requests.get(f"http://localhost/api/get_devices?lang=en&user_api_hash={api_hash}").json()
    dictobject = jsonobj[0]
    items = dictobject["items"]
    for item in items:
        
        resposedict = {
    'vehicleId' : '',
    'lat' : '',
    'long' : '',
    'timestamp' : '',
    'speed' : '',
    'engineStatus' : '',
    'locationame' : '',
    'VehicleDirectionAngle' : '',
    'fueldata' : ''
}
        if item['name'] in vehicleids:
            address = requests.get(f'http://osm.autotel.pk:8080/reverse?format=geojson&lat={item["lat"]}&lon={item["lng"]}').json()
            features = address['features']
            
            features1 = features[0]
            properties = features1['properties']
            #print(features1)
            display_address = properties['display_name']

            resposedict['vehicleId'] = item['name']
            resposedict['lat'] = item["lat"]
            resposedict['long'] = item["lng"]
            resposedict['timestamp'] = item["timestamp"]
            resposedict['engineStatus'] = item["online"]
            resposedict['speed'] = item["speed"] 
            resposedict['locationame']  =  display_address
            resposedict['VehicleDirectionAngle'] = item['course']
            resposedict['fueldata'] = '' #..
            responselist.append(resposedict)
    return responselist

@api.get("/detail_history")
def detail_history(clientid, vehicleid, datefrom, dateto):
    
    tablename = f'positions_{vehicleid}'
    vehicleHistory = []
    # Connect to the database
    cnx = pymysql.connect(
        host="localhost",
        user="root",
        password="hash4",
        database="hypegps_traccar"
        #group="hypegps"
    )
    # Create a cursor object
    cursor = cnx.cursor()

    # Execute the SHOW TABLES query
    cursor.execute(f"SHOW TABLES LIKE '{tablename}'")

    # Fetch the results
    results = cursor.fetchall()
    print(f'length of tupple {len(results)}')
    # Print the results
    if len(results) > 0:
        cursor.execute(f"SELECT * FROM `{tablename}` WHERE `time` BETWEEN '{datefrom} 00:00:00' AND '{dateto} 23:59:59'")
        rows = cursor.fetchall()
        #rows = cursor.execute(f"SELECT * FROM '{tablename}' WHERE 'time' BETWEEN '{datefrom} 00:00:00' AND '{dateto} 23:59:59'")
        
        for row in rows:
            history = {}
            '''
            address = requests.get(f'http://osm.autotel.pk:8080/reverse?format=geojson&lat={row[4]}&lon={row[5]}').json()
            features = address['features']
            
            features1 = features[0]
            properties = features1['properties']
            #print(features1)
            display_address = properties['display_name']
            '''
            history['lat'] = row[4]
            history['long'] = row[5]
            match = re.search(r"<ignition>(\w+)</ignition>", row[6])
            history['timestamp'] = row[9]
            history['speed'] = row[8]
            history['engineStatus'] = match.group(1)
            history['Location name'] = ''
            history['Fuel Data'] = ''
            history['Vehicle direction angle'] = row[3]
            vehicleHistory.append(history)
            
    else:
        print('No Vehicle data found.')
    #print(vehicleHistory)
    cursor.close()
    cnx.close()
    responselist = []
    api_hash = "$2y$10$B3j6pYUWdewxAiiXJA4KW.Q6j8I7J5UmUWG0EtT9SWz79xKAFnaF."
    jsonobj = requests.get(f"https://tracknow.pk/api/get_devices?lang=en&user_api_hash={api_hash}").json()
    dictobject = jsonobj[0]
    items = dictobject["items"]
    for item in items:
        resposedict = {
    'vehicleId' : '',
    'lat' : '',
    'long' : '',
    'timestamp' : '',
    'speed' : '',
    'engineStatus' : '',
    'locationame' : '',
    'VehicleDirectionAngle' : '',
    'fueldata' : ''
}
        if item['id'] == int(vehicleid):
            resposedict['vehicleId'] = item['name']
            resposedict['lat'] = item["lat"]
            resposedict['long'] = item["lng"]
            resposedict['timestamp'] = item["timestamp"]
            resposedict['engineStatus'] = item["online"]
            resposedict['speed'] = item["speed"]
            responselist.append(resposedict)
    return  vehicleHistory

@api.get("/violations/")
def get_voilations(clientid, vehicleid, datefrom, dateto):
    voilationslist = []
    api_hash = "$2y$10$B3j6pYUWdewxAiiXJA4KW.Q6j8I7J5UmUWG0EtT9SWz79xKAFnaF."
    jsonobj = requests.get(f"https://tracknow.pk/api/get_events?lang=en&device_id={vehicleid}&user_api_hash={api_hash}&date_from={datefrom}&date_to={dateto}").json()
    items = jsonobj['items']
    for item in items['data']:
        voilationdict = {}
        if not item['message'] == 'Ignition ON' and not item['message'] == 'Ignition OFF':
            voilationdict['voilation'] = item['message']
            voilationdict['timestamp'] = item['time']
            voilationdict['lat'] = item['latitude']
            voilationdict['long'] = item['longitude']
            voilationdict['engineStatus'] = 'ON'
            additional = item['additional']
            voilationdict['speed'] = additional['overspeed_speed']
            voilationdict['Location name'] = item['longitude']
            address = requests.get(f'http://osm.autotel.pk:8080/reverse?format=geojson&lat={item["latitude"]}&lon={item["longitude"]}').json()
            features = address['features']
            
            features1 = features[0]
            properties = features1['properties']
            #print(features1)
            display_address = properties['display_name']
            voilationdict['Location name'] = display_address
            voilationdict['Fuel Data']  = ''
            voilationslist.append(voilationdict)


    return voilationslist

