from fastapi import FastAPI
import json
import requests


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
    return  responselist

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

