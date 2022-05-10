import os, sys
import requests
import urllib.request
import folium
from folium.plugins import MarkerCluster
import io
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import *
import design

class GUIApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    
    def __init__(self, parent=None):
    
        super().__init__()
        self.setupUi(self)  #
        self.pushButton.clicked.connect(self.location_map)
        self.location_ip()
        input = self.lineEdit.text()
    def location_map(self):
        try:
            input = self.lineEdit.text()
            ip = str(input)
            print(ip)
            response = requests.get(
                url=f'http://ip-api.com/json/{ip}').json()
            # print(response)
            data = {

                '[Lat]': response.get('lat'),
                '[Lon]': response.get('lon'),
            }

            lat = data['[Lat]']
            lon = data['[Lon]']

            coordinate = (float(lat), float(lon))
            map = folium.Map(
                zoom_start=10, location=coordinate)
            folium.Marker(location=coordinate).add_to(map)

            # save map data to data object
            data_res = io.BytesIO()
            map.save(data_res, close_file=False)
            self.webView.setHtml(data_res.getvalue().decode())
        except:
            pass
    def location_ip(self):

        external_ip = urllib.request.urlopen(
            'http://ident.me').read().decode('utf8')
        response = requests.get(
            url=f'http://ip-api.com/json/{external_ip}').json()
        # print(response)
        data = {

            '[Lat]': response.get('lat'),
            '[Lon]': response.get('lon'),
        }

        lat = data['[Lat]']
        lon = data['[Lon]']

        coordinate = (float(lat), float(lon))
        map = folium.Map(
            zoom_start=10, location=coordinate)
        folium.Marker(location=coordinate, icon=folium.Icon(
            color='green')).add_to(map)

        # save map data to data object
        data_res = io.BytesIO()
        map.save(data_res, close_file=False)
        self.webView.setHtml(data_res.getvalue().decode())
   
def main():
    app = QtWidgets.QApplication(sys.argv) 
    window = GUIApp()  
    window.show()  
    app.exec_()  
if __name__ == "__main__":
    main()
