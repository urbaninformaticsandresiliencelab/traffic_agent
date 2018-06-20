# coding: utf-8
#!/usr/bin/env python3
import rx
from rx import Observable, Observer
from rx.subjects import Subject
import googlemaps
from datetime import datetime, timedelta
import io
import os
from selenium import webdriver
import time
def makeHtmlTrafficMap(lat, lon):
    try:
        os.remove("alocation.html")
    except FileNotFoundError:
        print("file not found")
        pass
    with io.open("alocation.html","a") as fw:
        fw.write("""<!DOCTYPE html>
            <html>
              <head>
                <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                <meta charset="utf-8">
                <title>Traffic layer</title>
                <style>
                  /* Always set the map height explicitly to define the size of the div
                   * element that contains the map. */
                  #map {
                    height: 100%;
                  }
                  /* Optional: Makes the sample page fill the window. */
                  html, body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                  }
                </style>
              </head>
              <body>
                <div id="map"></div>
                <script>
                  function initMap() {
                    var map = new google.maps.Map(document.getElementById('map'), {
            """)
        fw.write(f"zoom: 14,")
        fw.write("center: {lat: ")
        fw.write("{0}".format(lat))
        fw.write(", lng: ") 
        fw.write("{0}".format(lon))
        fw.write("""}
        });
                    var trafficLayer = new google.maps.TrafficLayer();
                    trafficLayer.setMap(map);
                  }
                </script>
                <script async defer
                src="https://maps.googleapis.com/maps/api/js?key=AIzaSyC3AwtAm23rleosJ_npXy1yTbX1aijdalI&callback=initMap">
                </script>
              </body>
            </html>
        """)
        fw.close()
def takeScreenShot(nw, webdriverpath):
    DRIVER = webdriverpath
    driver = webdriver.Chrome(DRIVER)
    driver.get(f"file://{os.getcwd()}/alocation.html")
    time.sleep(5)
    screenshot = driver.save_screenshot(f"{nw}.png")
    driver.quit()
class Agent(Observer):
    def gm_conf(self,apikey,an_origin,a_destination, webdriverpath):
#         print("init agent")
        self.__apikey = apikey
        self.an_origin = an_origin
        self.a_destination = a_destination
        self.gmaps = googlemaps.Client(key=f"{self.__apikey}")
        self.__data = list()
        self.__times_l = list()
        self.__duration_in_traffic_l = list()
        self.__duration_l = list()
        self.__webdriverpath = webdriverpath
    
    def getRoute(self,from_point, to_point):
        now = datetime.now()
        print(now)
        directions_result = self.gmaps.directions(origin=from_point,
                                             destination=to_point,
                                             mode="driving",
                                             departure_time=now)
        self.directions_result = directions_result
        print(len(self.directions_result))
        print(len(self.directions_result[0]["legs"]))
        
        print(self.directions_result[0]["legs"][0]["duration_in_traffic"]['text'])
        self.__data.append(dict(duration_in_traffic=self.directions_result[0]["legs"][0]["duration_in_traffic"],duration=self.directions_result[0]["legs"][0]["duration"]))
        self.__times_l.append(now)
        self.__duration_in_traffic_l.append(self.directions_result[0]["legs"][0]["duration_in_traffic"])
        self.__duration_l.append(self.directions_result[0]["legs"][0]["duration"])
        makeHtmlTrafficMap((float(self.an_origin.split(', ')[0]) + float(self.a_destination.split(', ')[0]) )/2,(float(self.an_origin.split(', ')[1]) + float(self.a_destination.split(', ')[1] ))/2)
        takeScreenShot(now, self.__webdriverpath)
    def on_next(self, value):
        return self.getRoute(self.an_origin, self.a_destination)
    def on_completed(self):
        times_l = list()
        duration_in_traffic_l = list()
        duration_l = list()
        print(self.__data)
        print("Done!")
    def on_error(self, error):
        print("Error Occurred: {0}".format(error))
