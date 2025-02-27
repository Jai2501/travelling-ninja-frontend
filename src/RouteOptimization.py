import json
import math
from collections import deque
from pprint import pprint
from random import random
from time import sleep
import csv
import urllib.request
import urllib.parse
from math import sin, cos, sqrt, atan2, radians
#import geopy.distance

apiKey = "AIzaSyBT-PLMwvnxCHS3ABKjjIwu4nRiydpe01c"
url = "https://maps.googleapis.com/maps/api/distancematrix/json?"

payload={}
headers = {}

format = "origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"

# A cluster of clusters
class Map:
    clusters = deque([])
    seenNodes = set()

    def __init__(self, fileName, radius):
        mapData = MapData(fileName)
        latitudes = mapData.returnLatitudes()
        longitudes = mapData.returnLongitudes()

        #allNodes = deque([])

        for i in range(0, len(latitudes)):
            node = Node(latitudes[i], longitudes[i])

            if (node.returnLatitude(), node.returnLongitude()) in self.seenNodes:
                node.incrementParcels()
                continue
            else:
                self.seenNodes.add((node.returnLatitude(), node.returnLongitude()))

            #allNodes.append(node)
        
            if len(self.clusters) == 0:
                cluster = Cluster(node, radius)
                self.clusters.append(cluster)
            else:
                foundClusterForNode = False

                for c in self.clusters:
                    if c.isValidClusterForNode(node) and (not foundClusterForNode):
                        c.addNewNodeToCluster(node)
                        foundClusterForNode = True
                        continue
                
                if not foundClusterForNode:
                    cluster = Cluster(node, radius)
                    self.clusters.append(cluster)
        
    def addNewCluster(self, cluster):
        self.clusters.append(cluster)
    
    def returnClusters(self):
        return self.clusters
    
# A cluster of Nodes
class Cluster:
    nodes = deque([])
    radiusOfCluster = 0
    centreOfCluster = (0, 0)

    def __init__(self, node, radius):
        self.nodes.append(node)
        self.radiusOfCluster = radius
        self.calculateClusterCentre()

    def addNewNodeToCluster(self, node):
        self.nodes.append(node)
        self.calculateClusterCentre()
    
    def returnNodesOfTheCluster(self):
        return self.nodes
    
    def returnCentreOfCluster(self):
        return self.centreOfCluster
    
    def returnTotalNumberOfParcels(self):
        totalParcels = 0

        for n in self.nodes:
            totalParcels += n.returnNumberOfParcels()
        
        return totalParcels

    def calculateClusterCentre(self):
        centreLatitude = 0
        centreLongitude = 0

        for node in self.nodes:
            centreLatitude += node.returnLatitude()
            centreLongitude += node.returnLongitude()
        
        centreLatitude = centreLatitude / len(self.nodes)
        centreLongitude = centreLongitude / len(self.nodes)

        self.centreOfCluster = (centreLatitude, centreLongitude)
        
    def isValidClusterForNode(self, node):
        # Euclidean Distance
        # latitudeDifference = abs(node.returnLatitude() - self.centreOfCluster[0])
        # longitudeDifference = abs(node.returnLongitude() - self.centreOfCluster[1])

        # latitudeDifference = pow(latitudeDifference, 2)
        # longitudeDifference = pow(longitudeDifference, 2)

        # euclideanDistance = math.sqrt(latitudeDifference + longitudeDifference)

        # geopy.distance.VincentyDistance((self.centreOfCluster[0], self.centreOfCluster[1]),(node.returnLatitude(), node.returnLongitude())).km 
        #return euclideanDistance <= ((self.radiusOfCluster / 40000) * 360)

        approxRadiusOfEarth = 6373.0

        centreLatitude = radians(self.centreOfCluster[0])
        centreLongitude = radians(self.centreOfCluster[1])

        pointLatitude = radians(node.returnLatitude())
        pointLongitude = radians(node.returnLongitude())

        differenceInLatitude = pointLatitude - centreLatitude
        differenceInLongitude = pointLongitude - centreLongitude

        temp = (sin(differenceInLatitude / 2) **  2) + (cos(centreLatitude) * cos(pointLatitude)) * (sin(differenceInLongitude / 2) ** 2)
        distanceInCoordinates = 2 * atan2(sqrt(temp), sqrt(1 - temp))

        distanceInKM = approxRadiusOfEarth * distanceInCoordinates
        # If true, can add new node
        return distanceInKM <= self.radiusOfCluster
        

# Points on Map
class Node:
    latitude = 0
    longitude = 0
    parcels = 0
    # can add additional details if want like, area name, pincode and stuff

    def __init__(self, lat, long):
        self.latitude = lat
        self.longitude = long
        self.parcels = 1
    
    def returnLongitude(self):
        return self.longitude
    
    def returnLatitude(self):
        return self.latitude

    def returnNumberOfParcels(self):
        return self.parcels
    
    def incrementParcels(self):
        self.parcels += 1

class MapData:
    
    latitudes = deque([])
    longitudes = deque([])

    def __init__(self, fileName):
        with open(fileName, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            i = 0

            for row in reader:
                if i == 0:
                    i += 1
                    continue
                else:
                    self.latitudes.append(row[4])
                    self.longitudes.append(row[5])
    
    def addMoreDataFrom(self, fileName):
        with open(fileName, 'r') as file:
            reader = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            i = 0

            for row in reader:
                if i == 0:
                    i += 1
                    continue
                else:
                    self.latitudes.append(row[4])
                    self.longitudes.append(row[5])
    
    def returnLatitudes(self):
        return self.latitudes
    
    def returnLongitudes(self):
        return self.longitudes

# "origins=40.6655101%2C-73.89188969999998&destinations=40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY"
class Algorithm:

    visited = set()

    def __init__(self):
        pass

    def distanceBetweenCluster(self, clusterOne, clusterTwo):
        #tempUrl = url + "origins=" + str(clusterOne[0]) + "%2C" + str(clusterOne[1]) + "&destinations=" + str(clusterTwo[0]) + "%2C" + str(clusterTwo[1]) + "&key=" + apiKey
        #response = urllib.request.urlopen(tempUrl)
        #result = json.load(response)
        #pprint(result)
        return random() * 1000
    
    def heuristicFunction(self, map, cluster):
        clusters = map.returnClusters()

        minDistance = float('inf')
        maxDistance = float('-inf')

        minCluster = None

        minNumberOfParcels = float('inf')
        maxNumberOfParcels = float('-inf')

        for c in clusters:
            if c not in self.visited:
                distance = self.distanceBetweenCluster(cluster.returnCentreOfCluster(), c.returnCentreOfCluster())

                if distance > maxDistance:
                    maxDistance = distance
                
                if distance < minDistance:
                    minDistance = distance
                    minCluster = c
        
        self.visited.add(c)
        return (c, minDistance)
    
    def runAlgorithm(self, map):
        clusters = map.returnClusters()
        path = deque([])

        for c in clusters:
            path.append(self.heuristicFunction(map, c))
        
        return path


map = Map("delivery_2022_12_14.csv", 2)
algorithm = Algorithm()
path = algorithm.runAlgorithm(map)

for p in path:
    print(p[0].returnCentreOfCluster(), p[1])
                

                

                





        
        
        


# n = Algorithm()
# n.distanceBetweenCluster((1, 2), (3, 4))