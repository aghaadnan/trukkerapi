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
    api_hash = "$2y$10$V4FYXIiJwyDbBmnk20XzvemcrFHvofHp0zt80qVUQoWLUShXDH0oW"
    #jsonobj = requests.get(f"http://localhost/api/get_devices?lang=en&user_api_hash={api_hash}").json()
    jsonobj = requests.get(f"http://world.autotel.pk/api/get_devices?lang=en&user_api_hash={api_hash}").json()
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
        device_data = item['device_data']
        if str(device_data['imei']) in vehicleids:
            address = requests.get(f'http://103.31.81.217:8080/reverse?format=geojson&lat={item["lat"]}&lon={item["lng"]}').json()
            features = address['features']
            
            features1 = features[0]
            properties = features1['properties']
            #print(features1)
            display_address = properties['display_name']

            resposedict['vehicleId'] = str(item['id'])
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
    
    imei = ""
    api_hash = "$2y$10$V4FYXIiJwyDbBmnk20XzvemcrFHvofHp0zt80qVUQoWLUShXDH0oW"
    jsonobj = requests.get(f"http://world.autotel.pk/api/get_devices?lang=en&user_api_hash={api_hash}").json()
    dictobject = jsonobj[0]
    items = dictobject["items"]
    responselist = []
    vehicleHistory = []
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
        device_data = item['device_data']
        
        imei = device_data['imei']
        print(imei)
        if str(device_data['imei']) == str(vehicleid):
            resposedict['vehicleId'] = item['name']
            resposedict['lat'] = item["lat"]
            resposedict['long'] = item["lng"]
            resposedict['timestamp'] = item["timestamp"]
            resposedict['engineStatus'] = item["online"]
            resposedict['speed'] = item["speed"]
            responselist.append(resposedict)
            vid = str(item['id'])
            
            tablename = f'positions_{vid}'
            
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
             
                    history['lat'] = row[4]
                    history['long'] = row[5]
                    match = re.search(r"<ignition>(\w+)</ignition>", row[6])
                    history['timestamp'] = row[9]
                    history['speed'] = row[8]
                    history['engineStatus'] = match.group(1)
                    history['Location name'] = ''#display_address
                    history['Fuel Data'] = ''
                    history['vector_angle'] = row[3]
                    history['temprature'] = ''
                    vehicleHistory.append(history)
            
            else:
                print('No Vehicle data found.')
            #print(vehicleHistory)
            cursor.close()
            cnx.close()
        else:
            print('No Vehicle data found.')
            #asdasdasd
                  
    return  vehicleHistory
@api.get("/violations/")
def get_voilations(clientid, vehicleid, datefrom, dateto):
    voilationslist = []
    api_hash = "$2y$10$V4FYXIiJwyDbBmnk20XzvemcrFHvofHp0zt80qVUQoWLUShXDH0oW"
    jsonobj = requests.get(f"http://world.autotel.pk/api/get_devices?lang=en&user_api_hash={api_hash}").json()
    dictobject = jsonobj[0]
    items = dictobject["items"]
    responselist = []
    vehicleHistory = []
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
        device_data = item['device_data']
        
        imei = device_data['imei']
        print(imei)
        if str(device_data['imei']) == str(vehicleid):
            resposedict['vehicleId'] = item['name']
            resposedict['lat'] = item["lat"]
            resposedict['long'] = item["lng"]
            resposedict['timestamp'] = item["timestamp"]
            resposedict['engineStatus'] = item["online"]
            resposedict['speed'] = item["speed"]
            responselist.append(resposedict)
            vid = item['id']
            #APIURL1= f"https://tracknow.pk/api/get_events?lang=en&device_id={vid}&user_api_hash={api_hash}&date_from={datefrom}&date_to={dateto}"
            #print(APIURL1)
            jsonobj1 = requests.get(f"http://world.autotel.pk/api/get_events?lang=en&device_id={vid}&user_api_hash={api_hash}&date_from={datefrom}&date_to={dateto}").json()
            
            items = jsonobj1['items']
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
                    address = requests.get(f'http://103.31.81.217:8080/reverse?format=geojson&lat={item["latitude"]}&lon={item["longitude"]}').json()
                    features = address['features']
                    
                    features1 = features[0]
                    properties = features1['properties']
                    #print(features1)
                    display_address = properties['display_name']
                    voilationdict['Location name'] = display_address
                    voilationdict['Fuel Data']  = ''
                    voilationslist.append(voilationdict)

        else:
            print('No Vehicle data found.')
    return voilationslist

