
# coding: utf-8

# In[1]:


##############
#Dependencies#
##############

import os                                        ### import operating system ###
import xml.etree.ElementTree as ET               ### xml.etree is a flexible container object,
import gzip                                      ### compress and decompress gzip files ###
import time                                      ### import time libraries ###
import requests                                  ### Libraries to support HTML requests in python ###
import pandas
from  send_email_with_attachments import send_an_email, EMAIL_ADDRESS, PASSWORD


# In[2]:

####################################################################
# Defenition to pull Incident Reports and Traffic Detectors from MN DOT
####################################################################
# Request incident information - xml.gz file
# Open, decompress, and decode
# Request traffic detector information - xml.gz file
# Open, decompress, and decode

def download():
    i = requests.get('http://data.dot.state.mn.us/iris_xml/incident.xml.gz')
    with open('data/XMLs/incidents.xml', 'w') as handle:
        handle.write(gzip.decompress(i.content).decode('utf-8'))

    s = requests.get('http://data.dot.state.mn.us/iris_xml/stat_sample.xml.gz')
    with open('data/XMLs/station_sample.xml', 'w') as handle:
        handle.write(gzip.decompress(s.content).decode('ISO-8859-1'))


###################################################
# Defenition to convert information in DataFrames
###################################################
# Identify crash information, try to open csv file and convert to DF, save updated DF as csv
# Identify detector information, try to open as csv and convert to DF, save updated DF as csv



def data_check():
        try:
            with open('data/crash_data.csv', 'r') as CD:
                incidents()
        except FileNotFoundError:
                All_Crash_Data = pandas.DataFrame(columns=['Name', 'Date', 'DirectionLocation', 'Road', 'Event'])
                with open('data/crash_data.csv', 'w') as f:
                    All_Crash_Data.to_csv(f, header=True)
                    incidents()

        try:
            with open('data/station_data.csv', 'r') as CD:
                stations()
        except FileNotFoundError:
                station_data = pandas.DataFrame(columns=  ["Station","Heading", "Time","Order","Speed","Flow","Lat","Lng"])
                with open('data/station_data.csv', 'w') as f:
                    station_data.to_csv(f, header=True)
                    stations()


# In[4]:


###################################################
# Parse incident information and save into csv
###################################################

## Create lists, append lists if data exists otherwise enter NA, combine data as DF, save as csv

def incidents():
    dates = []
    incident_dirs = []
    roads = []
    locations = []
    names = []
    events = []

    XMLfile = "data/XMLs/incidents.xml"
    parsedXML = ET.parse(XMLfile)
    root = parsedXML.getroot()
    for child in root:
        try:
            dates.append(child.attrib['event_date'])
        except KeyError:
            dates.append("NA")
        try:
            names.append(str(child.attrib['name']))
        except KeyError:
            name.append("NA")
        try:
            incident_dirs.append(child.attrib['dir'])
        except KeyError:
            incident_dir.append("NA")
        try:
            roads.append(child.attrib['road'])
        except KeyError:
            roads.append('NA')
        try:
            locations.append(child.attrib['location'])
        except KeyError:
            locations.append("NA")
        try: 
            event = child.attrib['event_type'].split("_", 1)
            events.append(event[1])
        except KeyError:
            events.append("NA")


    DF = pandas.DataFrame({"Name" : names,
                       "Date" : dates,
                       "Direction": incident_dirs,
                       "Road" : roads,
                       "Location" : locations,
                       "Event" : events})


    print("Incident Data Parsed")

    with open('data/crash_data.csv', 'a') as f:
        DF.to_csv(f, header=False)


# In[5]:


###################################################
# Parse station information and save as csv
###################################################

## Create lists, append lists if data exists otherwise enter NA, combine data as DF, save as csv
def stations():
    stations = []
    times = []
    flows = []
    speeds = []
    order = []
    headings = []
    lats = []
    lngs = []
    with open('station_keys/Northbound_35W_StationNames.csv', 'r') as NB:
        
        NB_DF = pandas.read_csv(NB)
    with open('station_keys/Southbound_35W_StationNames.csv', 'r') as SB:
        SB_DF = pandas.read_csv(SB)
    
    XMLfile = "data/XMLs/station_sample.xml"
    parsedXML = ET.parse(XMLfile)
    root = parsedXML.getroot()
    for child in root:
    
        if child.attrib['sensor'] in NB_DF["1"].values :
            lats.append(NB_DF.loc[NB_DF['1'] == child.attrib['sensor']]['Lat'].values[0])
            lngs.append(NB_DF.loc[NB_DF['1'] == child.attrib['sensor']]['Lng'].values[0])
        
            headings.append("NB")
            order.append(NB_DF.loc[NB_DF['1'] == child.attrib['sensor']]['Order'].values[0])
            try:
                stations.append(child.attrib['sensor'])
            except KeyError:
                stations.append("NA")

            try:
                times.append(str(root.attrib['time_stamp']))
            except KeyError:
                times.append("NA")
            try:
                flows.append(child.attrib['flow'])
            except KeyError:
                flows.append("NA")

            try:
                speeds.append(child.attrib['speed'])
            except KeyError:
                speeds.append("NA")
           
        if child.attrib['sensor'] in SB_DF["1"].values:
            lats.append(SB_DF.loc[SB_DF['1'] == child.attrib['sensor']]['Lat'].values[0])
            lngs.append(SB_DF.loc[SB_DF['1'] == child.attrib['sensor']]['Lng'].values[0])
            headings.append("SB")
            order.append(SB_DF.loc[SB_DF['1'] == child.attrib['sensor']]['Order'].values[0])
            try:
                stations.append(child.attrib['sensor'])
            except KeyError:
                stations.append("NA")

            try:
                times.append(str(root.attrib['time_stamp']))
            except KeyError:
                times.append("NA")
            try:
                flows.append(child.attrib['flow'])
            except KeyError:
                flows.append("NA")

            try:
                speeds.append(child.attrib['speed'])
            except KeyError:
                speeds.append("NA")
            

    DF = pandas.DataFrame({"Station" : stations,
                       "Heading": headings,
                        "Time" : times,
                       "Order" : order,
                       "Speed" : speeds,
                       "Flow" : flows,
                      "Lat": lats,
                      "Lng" : lngs })
    with open(f'data/station_data.csv', 'w') as f:
           DF.to_csv(f, header=True)
    print("Station Data Parsed")
    
   


# In[6]:


def Route_Summary():
    try:
        Summary = pandas.read_csv('data/Route_Summary.csv')
    except FileNotFoundError:
        Summary = pandas.DataFrame(columns=["Heading", "Time","Order","Speed","Flow","Lat","Lng"])


        
    All_Station_Data = pandas.read_csv('data/station_data.csv')
#     All_Station_Data = All_Station_Data.set_index('Station')
    

    route = All_Station_Data.groupby('Station').head(1).index.values

    for station in route:
            Summary_partial = All_Station_Data.loc[station, 
                                                       ["Station","Heading", "Time","Order","Speed","Flow","Lat","Lng"]]
            Summary = Summary.append(Summary_partial,sort=True)
            Summary = Summary.replace("UNKNOWN",0)
            
 
    Summary = Summary.sort_values(['Station', 'Time'])
    with open('data/Route_Summary.csv', 'w') as f:
        Summary.to_csv(f,header=True, columns=["Station","Heading", "Time","Order","Speed","Flow","Lat","Lng"])
                       
    print("Summary Saved at data/Route_Summary.csv")
     


# In[1]:


def send_email_from_Heroku():
   try:
        filename="/Data/Route_Summary.csv"
        send_an_email(file_name,subject="Route_Summary.csv", body='from Python!')
        filename="Data/crash_data.csv"
        send_an_email(file_name,subject="sending email with attachments", body='from Python!')
   except FileNotFoundError:
        print("File not found, Is this the first time you ran this?")



# In[2]:


def Data_Request():
    send_email_from_Heroku()
    end_time =  t_end = time.time() + 1586400
    while time.time() < end_time:
        download()
        data_check()
        Route_Summary()
        print("sleeping 30s")
        time.sleep(30)
    send_email_from_Heroku()



#one time email for restart
Data_Request()

