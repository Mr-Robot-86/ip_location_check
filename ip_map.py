import os
import sys
import requests
import socket
import time
import json
import urllib.request
import folium
from folium.plugins import MarkerCluster
import io
from PyQt5 import QtWidgets
from PyQt5 import *
from PyQt5.QtCore import Qt, QTimer, QObject,  pyqtSignal
from datetime import datetime
import threading
import psutil
import design
import pandas as pd



def get_bandwidth_in():
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent
    net1_in = psutil.net_io_counters().bytes_recv

    time.sleep(1)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent
    net2_in = psutil.net_io_counters().bytes_recv

    # Compare and get current speed
    if net1_in > net2_in:
        current_in = 0
    else:
        current_in = net2_in - net1_in

    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out

    network = float(current_in)
    return network


def get_bandwidth_out():
    # Get net in/out
    net1_out = psutil.net_io_counters().bytes_sent

    time.sleep(1)

    # Get new net in/out
    net2_out = psutil.net_io_counters().bytes_sent

    # Compare and get current speed

    if net1_out > net2_out:
        current_out = 0
    else:
        current_out = net2_out - net1_out

    network = float(current_out)
    return network


def humansize(nbytes):
    suffixes = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s', 'PB/s']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

class Check_IP(QtCore.QObject):
    messageChanged = QtCore.pyqtSignal(str)
    messageChanged_1 = QtCore.pyqtSignal(str)
    messageChanged_2 = QtCore.pyqtSignal(str)

    def check(self):
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        while True:
            sp_in = get_bandwidth_in()
            sp_out = get_bandwidth_out()
            external_ip = urllib.request.urlopen(
                'http://ident.me').read().decode('utf8')

            self.messageChanged.emit(humansize(sp_in))
            self.messageChanged_1.emit(humansize(sp_out))
            self.messageChanged_2.emit(external_ip)


class GUIApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
   
    def __init__(self, parent=None):

       
        super().__init__()
        self.setupUi(self)  #
        self.pushButton.clicked.connect(self.search_location_ip)
        
        input = self.lineEdit.text()
        self.check_ip = Check_IP()
        self.check_ip.messageChanged.connect(self.updateMessage)
        self.check_ip.messageChanged_1.connect(self.updateMessage_1)
        self.check_ip.messageChanged_2.connect(self.updateMessage_2)
        self.check_ip.check()
        
        self.check_dns_google()
        self.check_dns_cloudflare()

        self.visualization_ip_map()

    @QtCore.pyqtSlot(str)
    def updateMessage(self, message):
        self.label_3.setText(message)
        self.label_3.adjustSize()

    @QtCore.pyqtSlot(str)
    def updateMessage_1(self, message):
        self.label_4.setText(message)
        self.label_4.adjustSize()

    @QtCore.pyqtSlot(str)
    def updateMessage_2(self, message):
        self.label_9.setText(message)
        self.label_9.adjustSize()

    

    def get_ip_by_hostname(self):
        input = self.lineEdit.text()
        input_out = input
        try:
            float(input_out)
            ip = str(input_out)
        except:
            ip = socket.gethostbyname(input_out)
            return ip

    def search_location_ip(self):
        try:
            input = self.lineEdit.text()
            input_out = input
            self.get_ip_by_hostname()

            ip = self.get_ip_by_hostname()

            response = requests.get(
                url=f'http://ip-api.com/json/{ip}').json()
            # print(response)
            data_response = {
                '[IP]': response.get('query'),
                '[Lat]': response.get('lat'),
                '[Lon]': response.get('lon'),
                '[City]': response.get('city'),
            }
            # print(data)
            lat = data_response['[Lat]']
            lon = data_response['[Lon]']
            ip_guery = data_response['[IP]']
            city = data_response['[City]']
            coordinate = (float(lat), float(lon))
            js_data = ip_guery, lat, lon, city
            with open("ip_gps.txt", "a") as file:
                print(js_data, end='\n', file=file)
            map = folium.Map(
                zoom_start=10, location=coordinate)
            folium.Marker(location=coordinate).add_to(map)

            # save map data to data object
            data_res = io.BytesIO()
            map.save(data_res, close_file=False)
            self.webView.setHtml(data_res.getvalue().decode())
        except:
            pass


    def check_dns_google(self):
        try:
            r = requests.get("https://dns.google.com")
            r.raise_for_status()

            self.label_7.setStyleSheet("color: rgb(0, 255, 0);")

        except:
            self.label_7.setStyleSheet("color: rgb(255, 0, 0);")

    def check_dns_cloudflare(self):
        try:
            r = requests.get("http://1.1.1.1")
            r.raise_for_status()

            self.label_8.setStyleSheet("color: rgb(0, 255, 0);")

        except:
            self.label_8.setStyleSheet("color: rgb(255, 0, 0);")

    def visualization_ip_map(self):
        try:
            external_ip = urllib.request.urlopen(
                'http://ident.me').read().decode('utf8')
            response = requests.get(
                url=f'http://ip-api.com/json/{external_ip}').json()
            # print(response)
            data_s = {
                '[IP]': response.get('query'),
                '[Lat]': response.get('lat'),
                '[Lon]': response.get('lon'),
                '[City]': response.get('city'),
            }
            Lat = data_s['[Lat]']
            Lon = data_s['[Lon]']
            IP = data_s['[IP]']
            coordinate = (float(Lat), float(Lon))
            map = folium.Map(zoom_start=10, location=coordinate)

            data = pd.read_csv( "ip_gps.txt")
            lat = data['LAT']
            lon = data['LON']
            ip_data = data['IP']
            ip = ip_data
            for lat, lon, ip in zip(lat, lon, ip):
                folium.Marker(location=[float(lat), float(lon)], popup=str(
                    ip.strip("',',(")),   icon=folium.Icon(color='gray')).add_to(map)
            folium.Marker(location=coordinate, popup=str(
                IP), radius=100, icon=folium.Icon(color='green')).add_to(map)
            folium.CircleMarker(location=coordinate, radius=50).add_to(map)
            data_res = io.BytesIO()
            map.save(data_res, close_file=False)
            self.webView.setHtml(data_res.getvalue().decode())
        except:
            pass


def main():
    app = QtWidgets.QApplication(sys.argv)  
    window = GUIApp()  
    window.show()  
    app.exec_() 

if __name__ == "__main__":
    main()
