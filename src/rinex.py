import subprocess
import threading
import os
import numpy as np
import shutil
import time
import serial
from datetime import datetime
import requests
import dropbox
import math
import firebase_admin
from firebase_admin import credentials,db
import tkinter as tk
from tkinter import font
import time

# Gunakan Access Token Dropbox yang sudah Anda miliki
access_token = "sl.u.AF39ujNQ2-7XwQjo5VYQiVlC56i4urIO6iF0SQ3zQd7578Ub1cWz6SuXfGtN1DICaDQ4GE_18_J31pD4lT1h4UBsRlBu35mCeMrBqBMq1kwTS3NDyfZQ8c9Jyh7_itcoscskjNltwkY9xeeOSKt-wXVohLyXepryyPEmC9KFQvtDlRzeXyPd8AkdLdbIyUhr6u2ldPPEkIAI4xuhk19JlP1C4wGe9gh_Ew6WHPd9aQEqNEqmx_-ntEIvc3D0sxb0uFs0xqLy2COUl8iBdZeLXty--WFdbppcVMT9N6sUq3PHJ-YZB7lD4L9hIlBPsSbeNiJ56tJIEiaguiLUIIhgk1jV4jE7AyE2tohpy441U3FLGovwx3CTnvsi7NILfTeslXC0wWhJmNcK5irILuDcWH38udYiGGwSxCt0YP8XCFYXvOyTGZ9fbCcC3iwFGB5m2PvVaoCbSXwJxiVlgfAJrVEdEJXPJ0Q2dKTTRwDyEy-B-ofeNbv7clXZoj6ydRXZ9ntO4ROUV-UNEWWv6M1qoxHIGq0pCh_L_T7urd_UAZ1_KAi-w114VssWDL2SsdtP4kBeyDfDm88ubxBvUryZZZ7PD7K_4DmBhujTHyX_JxLi-_4yuwGiemkAMIv1ZKnMcCuaZG_5xLaAzfNpZrUUE4kaVOCQm0h8NNuRw4dhncmdWkTqpsqPzKUe1gMu-HBo12vc7OlLsCYj4MH5Gn3Gfxan6dRk5g8o5B4CpAnYDoUuWqGEMkhJIuf9nnRKzxVgqpKT4fhwVgumGbYzSbeqs2D4QDx3R10ZHBhm2XNIlDfOOUN_OKIyTzbXfB1k6wKGrJBFSD8fRB9aPF7RIwWHUXLfBCouB8JgJzn8YrmBzUJOyaFONplbqBxy1Sh9Qj1UFVap5vlwQvwPS94oaDLWFfRp03jEV_rD8SxHOx957TuXyUCPQ58puomuh_jYEBOl06wsK2G9wOcqY6LgfrDI4boGiPGX8eQ2tgaE2z-vntLfmJJC6RusenPHMeZRXdcRg4I1pGWM2SGQGLkhgIiOEVOf5sV0af6C4K8ZYJ4eGnFKcbW21dbFW657A3WLD_zG27e_hH1F0LpiKqpnD4YbWzQR2D-Ez7M3lm-U9XK0UYGAES4HiSWhECAYDYYCmpCPfq43xyBPiFKMBtpX4doC9qrO57UEXQbSuvXIaZxMmZoQToDWOSV0EpWC8LJwjks9PhhwOdr8jU5dD7zzfWMFUUhHFpNUGrt2LB2MlQ1JTFKYYLudWf1pnWqjD-ryHUF81UCIbHuO-SVX8XvCkkuAni_O5x-C04YlXBio3a-fePHEm9XJJP_NcSwoYzvYmfJff3lmFxQLIoXkHMjgF590qdk7VJr--fcXZPpAmZu6Rb7656MQ1N2AYRa66rrLawaqGjVmfLBQ4bmi0OeaSktFqqQt"

#Cholid
cred_ppls = credentials.Certificate('/home/ronny/asset/ppls-app.json')
ppls_app = firebase_admin.initialize_app(cred_ppls, {
    'databaseURL': 'https://ppls-app-default-rtdb.firebaseio.com/'  # Replace with your database URL    
})

# Configuration parameters
device_port = "/dev/ttyGPS"  # Update this to the correct port for your ZED-F9P
baud_rate = "115200"          # Default baud rate for ZED-F9P
output_raw_file = "/home/ronny/gnss-rover/output.ubx"  # Temporary raw file
output_rinex_file = "/home/ronny/gnss-rover/output.obs"    # Final RINEX observation file
output_rinex_file_nav = "/home/ronny/gnss-rover/output.nav"    # Final RINEX observation file
output_folder = "/home/ronny/gps-record"
tcp_port = 9000
# DROPBOX PARAMS
auth_code = "tydj37Ufg54AAAAAAAAAf8-wu05VAM_49_4-jKINzi8"
redirect_uri = "http://localhost:8081/"
app_key = "2cjumlwvnf01wd7"
app_secret = "i6nm76s8yy9tqrm"
refresh_token = "aPyJmpqx6k4AAAAAAAAAATK0QfHt8jv1g6zHkW2F2vUkQ5DmTc2bZuGd4lZQ1hj"

str2str_command = [
        f"str2str",
        "-in", f"{device_port}",
        "-out", f"tcpsvr://:{tcp_port}",
        "-out", f"file://{output_raw_file}",
    ]
rtkrcv_command = [
    "rtkrcv",
    "-o", "/home/ronny/gnss-rover/ntrip1.conf",  # Path to rtkrcv configuration
    "-s"                                       # Start immediately
]
def send_ubx_message(ser, message):
    ser.write(message)
    print(f"Sent: {message.hex()}")
def collect_raw_data(duration):
    """
    Collect raw GNSS data from ZED-F9P using RTKLIB's str2str.
    """
    print("Collecting raw data from ZED-F9P...")
    str2str_command = [
        f"str2str",
        "-in", f"serial:///ttyGPS:115200:8:n:1",
        "-out", f"tcpsvr://:{tcp_port}",
        "-out", f"file://{output_raw_file}",
        "-msg", "1003,1004,1011,1012,1019,1020,1045,1044,1046,1074,1084,1094,1124,1077,1087,1097,1127"
    ]
    
    try:
        subprocess.run(str2str_command, check=True, timeout=duration)
        print(f"Raw data collected in file: {output_raw_file}")
    except subprocess.TimeoutExpired:
        print(f"Data collection timed out after {duration} seconds. Proceeding with the program...")
    # except TimeoutError as e:
    #     pass
    except subprocess.CalledProcessError as e:
        print(f"Error during raw data collection: {e}")
    #     exit(1)
def run_rtkrcv():
    """
    Run RTK navi with rtkrcv.conf.
    """
    run_status_rcv = 0
    while True:
        ref = db.reference('Realtime')
        data = ref.child("rover").get()
        interval = data['Interval']
        duration = (60*(interval-1))  # Time in seconds
        # print(duration)
        now = datetime.now()
        minute = now.strftime("%M")
        if minute == "00" or minute == "15" or minute == "30" or minute == "45":
            run_status_rcv = 1
        else:
            run_status_rcv = 0
        if run_status_rcv == 1:
            time.sleep(5)
            print("Starting RTKRCV...")
            rtkrcv_command = [
                "rtkrcv",
                "-o", "/home/ronny/gnss-rover/ntrip1.conf",  
                "-s"                                       
            ]
            try:
                subprocess.run(rtkrcv_command, check=True, timeout=duration)
                print(f"RTKRCV collected in file: {output_raw_file}")
            except subprocess.TimeoutExpired:
                print(f"RTKRCV timed out after {duration} seconds. Proceeding with the program...")
            except subprocess.CalledProcessError as e:
                print(f"Error during RTKRCV: {e}")
            time.sleep(15)
def run_rnx2rtkp():
    """
    Run RTK navi with rtkrcv.conf.
    """
    
    duration = (20)  # Time in seconds
    print(duration)
    print("Starting RNX2RTKP")
    
    rtkrcv_command = [
        "rnx2rtkp",
        "/home/ronny/gnss-rover/output1.obs",
        "/home/ronny/gnss-rover/base.obs",
        "/home/ronny/gnss-rover/output1.nav",
        "-k", "/home/ronny/gnss-rover/post.conf",
        "-o", "/home/ronny/gnss-rover/solution_post.pos"  # Path to rtkrcv configuration
    ]
    
    try:
        subprocess.run(rtkrcv_command, check=True, timeout=duration)
        print(f"RNX2RTKP Success created in: {output_raw_file}")
    except subprocess.TimeoutExpired:
        print(f"RNX2RTKP timed out after {duration} seconds. Proceeding with the program...")
        # subprocess.run("shutdown -y")
    # except TimeoutError as e:
    #     pass
    except subprocess.CalledProcessError as e:
        print(f"Error during RNX2RTKP: {e}")
    print("wait 20 second for next rcv")
    # time.sleep(8)
def convert_to_rinex():
    """
    Convert raw GNSS data to RINEX observation file using RTKLIB's convbin.
    """
    print("Converting raw data to RINEX format...")
    convbin_command = ["convbin", "-v", "2.11","-n",f"{output_rinex_file_nav}", "-f","1","-f","2",f"{output_raw_file}"]
    
    try:
        subprocess.run(convbin_command, check=True)
        print(f"RINEX observation file created: {output_rinex_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during RINEX conversion: {e}")
        exit(1)
def convert_to_rinex2():
    """
    Convert raw GNSS data to RINEX observation file using RTKLIB's convbin.
    """
    print("Converting raw data to RINEX format...")
    convbin_command = ["convbin", "-v", "2.11", "-o", f"{output_rinex_file}","-r","rtcm3", f"{output_raw_file}"]
    
    try:
        subprocess.run(convbin_command, check=True)
        print(f"RINEX observation file created: {output_rinex_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during RINEX conversion: {e}")
        exit(1)
def upload_file_to_dropbox(file_path, dropbox_path,access_token):
    # Connect to Dropbox
    dbx = dropbox.Dropbox(access_token)
    for i in range(0,10):
        try:
            with open(file_path, "rb") as file:
                # Upload and overwrite the file in the specified Dropbox path
                dbx.files_upload(file.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
                print(f"{file_path} has been updated in Dropbox at {dropbox_path}")
            break
        except Exception as e:
            time.sleep(2)
            print(f"fail {i}")
def get_access_and_refresh_token(auth_code, redirect_uri, app_key, app_secret):
    token_url = "https://api.dropbox.com/oauth2/token"
    
    response = requests.post(
        token_url,
        data={
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        },
        auth=(app_key, app_secret)
    )
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        print("Access token:", access_token)
        print("Refresh token:", refresh_token)
        return access_token, refresh_token
    else:
        print("Failed to get tokens:", response.json())
        return None, None
def get_access_token_from_refresh_token(refresh_token, app_key, app_secret):
    # Dropbox OAuth 2.0 token URL
    token_url = "https://api.dropbox.com/oauth2/token"
    
    # Send a POST request to get a new access token
    response = requests.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
        auth=(app_key, app_secret)  # Use app credentials for basic auth
    )
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("New Access Token:", access_token)
        return access_token
    else:
        print("Failed to refresh access token:", response.json())
        return None
def download_file_from_dropbox(LOCAL_FILE_PATH,DROPBOX_FILE_PATH,new_access_token):
    try:
        # Connect to Dropbox
        dbx = dropbox.Dropbox(new_access_token)

        # Check if the file already exists locally and delete it
        if os.path.exists(LOCAL_FILE_PATH):
            os.remove(LOCAL_FILE_PATH)
            print(f"Existing file '{LOCAL_FILE_PATH}' was removed.")

        # Download the file from Dropbox
        with open(LOCAL_FILE_PATH, 'wb') as f:
            metadata, res = dbx.files_download(DROPBOX_FILE_PATH)
            f.write(res.content)
        
        print(f"File downloaded successfully as {LOCAL_FILE_PATH}")
    except dropbox.exceptions.AuthError:
        print("ERROR: Invalid access token!")
    except dropbox.exceptions.ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
def upload_data_post():
    file_path = "/home/ronny/gnss-rover/solution_post.pos"
    a = 6378137.0  # Earth's semi-major axis in meters (WGS84)
    e2 = 0.00669437999014  # Earth's first eccentricity squared (WGS84)
    try:
        ref = db.reference('Realtime')
        data = ref.child("rover").get()
        index = data['index']
        ref = db.reference(f"Patok/{index}")
        data = ref.child("Realtime").get()
        lat_ref = data["lat"]
        lon_ref = data["long"]
        h_ref = data["alt"]
        upload_data = {
            "east": [],
            "north": [],
            "up": []
        }
        # Open the file and iterate through each line
        with open(file_path, 'r') as file:
            try:
                for line_number, line in enumerate(file, start=0):
                    # Strip whitespace characters from the ends
                    clean_line = line.strip()
                    # print(len(clean_line))
                    # print(clean_line)
                    if '%' in clean_line or len(clean_line)==0:
                        # time.sleep(1)
                        continue
                    parts = clean_line.split()
                    
                    date = parts[0].replace("/","-")
                    waktu = f"{date}_{parts[1][:-4]}"
                    
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    # print(date, waktu)
                    # print(x,y,z)
                    ref_ecef = geodetic_to_ecef(lat_ref, lon_ref, h_ref, a, e2)
                    x_ref, y_ref, z_ref = ref_ecef
                    rover_ecef = geodetic_to_ecef(x, y, z, a, e2)
                    x_rover, y_rover, z_rover = rover_ecef
                    delta = np.array([x_rover - x_ref, y_rover - y_ref, z_rover - z_ref])
                    lat_ref_rad = np.radians(lat_ref)
                    lon_ref_rad = np.radians(lon_ref)
                    rot_matrix = np.array([
                        [-np.sin(lon_ref_rad), np.cos(lon_ref_rad), 0],
                        [-np.sin(lat_ref_rad) * np.cos(lon_ref_rad), -np.sin(lat_ref_rad) * np.sin(lon_ref_rad), np.cos(lat_ref_rad)],
                        [np.cos(lat_ref_rad) * np.cos(lon_ref_rad), np.cos(lat_ref_rad) * np.sin(lon_ref_rad), np.sin(lat_ref_rad)]
                    ])
                    enu = np.dot(rot_matrix, delta)
                    # print(enu)
                    upload_data["east"].append({
                        f"{waktu}": enu[0]
                    })
                    upload_data["north"].append({
                        f"{waktu}": enu[1]
                    })
                    upload_data["up"].append({
                        f"{waktu}": enu[2]
                    })
            finally:
                east_data = {k: v for d in upload_data["east"] for k, v in d.items()}
                north_data = {k: v for d in upload_data["north"] for k, v in d.items()}
                up_data = {k: v for d in upload_data["up"] for k, v in d.items()}
                ref = db.reference(f"Patok/{index}/Storage")
                ref.child("east/labels").update(east_data)
                ref.child("north/labels").update(north_data)
                ref.child("up/labels").update(up_data)
                print(f"Data Updated on patok {index}")    
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
def start_rover():
    run_status = 0
    local_file_path = "/home/ronny/gnss-rover/output.obs"
    local_file_path_nav = "/home/ronny/gnss-rover/output.nav" # Path to your local .txt file
    local_file_path_pos = "/home/ronny/gnss-rover/solution1.pos" # Path to your local .txt file
    local_file_path_pos_post = "/home/ronny/gnss-rover/solution_post.pos" # Path to your local .txt file
    local_file_path_base = "/home/ronny/gnss-rover/base.obs" # Path to your local .txt file
    ref_status = db.reference(f"/Realtime/rover/")
    ref = db.reference(f"/Realtime/base/")
    data = {
        f"request": 1
    }
    ref.update(data)
    while True:
        ref = db.reference("/Realtime")
        data = ref.child("rover").get()
        mode = f"{data['mode']}"
        now = datetime.now()
        minute = now.strftime("%M")
        data_status = {
            f"status": "Standby"
        }
        ref_status.update(data_status)
        if minute == "00" or minute == "15" or minute == "30" or minute == "45" or mode =="1":
            run_status = 1
            ref = db.reference(f"/Realtime/base/")
            data = {
                f"request": 1
            }
            ref.update(data)
        else:
            run_status = 0
        print(run_status)
        if run_status == 1:
            data_status = {
                f"status": "Setting Up"
            }
            ref_status.update(data_status)
            run_status = 0
            ref = db.reference("/Realtime")
            data = ref.child("rover").get()
            index = data['index']
            interval = data['Interval']
            base_point = data['base']
            tanggal = now.strftime("%d-%m-%Y")
            label = now.strftime("%d-%m-%Y_%H:%M")
            str1 = now.strftime("%d%m")
            str2 = now.strftime("%H%M")
            str3 = now.strftime("%Y")
            filename = f"RVLP_{str1}_{str2}_{str3}.obs"
            filename_nav = f"RVLP_{str1}_{str2}_{str3}.nav"
            filename_pos = f"RVLP_{str1}_{str2}_{str3}.pos"
            duration = (60*(interval-2))  # Time in seconds
            data_status = {
                f"status": "Running..."
            }
            ref_status.update(data_status)
            collect_raw_data(duration)
            time.sleep(5)
            data_status = {
                f"status": "Running..."
            }
            ref_status.update(data_status)
            convert_to_rinex()
            convert_to_rinex2()
            shutil.copy("/home/ronny/gnss-rover/solution.pos","/home/ronny/gnss-rover/solution1.pos")
            shutil.copy("/home/ronny/gnss-rover/output.obs","/home/ronny/gnss-rover/output1.obs")
            shutil.copy("/home/ronny/gnss-rover/output.nav","/home/ronny/gnss-rover/output1.nav") 
            shutil.copy("/home/ronny/gnss-rover/solution.pos",f"/home/ronny/gps-record/{filename_pos}")
            shutil.copy("/home/ronny/gnss-rover/output.obs",f"/home/ronny/gps-record/{filename}")
            shutil.copy("/home/ronny/gnss-rover/output.nav",f"/home/ronny/gps-record/{filename_nav}") 
            data_status = {
                f"status": "Uploading Result..."
            }
            ref_status.update(data_status)
            new_access_token = access_token
            dropbox_destination_path = f'/GPS ZED-F9P/Rover/{filename}' 
            dropbox_destination_path_nav = f'/GPS ZED-F9P/Rover/{filename_nav}'
            dropbox_destination_path_pos = f'/GPS ZED-F9P/Rover/{filename_pos}'
            dropbox_destination_path_post = f'/GPS ZED-F9P/Rover/POST_{filename_pos}'
            upload_file_to_dropbox(local_file_path, dropbox_destination_path,new_access_token)
            upload_file_to_dropbox(local_file_path_nav, dropbox_destination_path_nav,new_access_token)
            upload_file_to_dropbox(local_file_path_pos, dropbox_destination_path_pos,new_access_token)
            if(base_point==1):
                ref = db.reference('Realtime',ppls_app)
                data = ref.child("base").get()
                dropbox_base_path = data['obs']
            else:
                ref = db.reference('Realtime')
                data = ref.child("base").get()
                dropbox_base_path = data['obs']
            data_status = {
                f"status": "Processing Result..."
            }
            ref_status.update(data_status)
            download_file_from_dropbox(local_file_path_base,dropbox_base_path,new_access_token)
            ref = db.reference(f"/Patok/{index}/Storage/obs")
            data = {
                f"{label}": dropbox_destination_path
            }
            ref.update(data)
            ref = db.reference(f"/Patok/{index}/Storage/nav")
            data = {
                f"{label}": dropbox_destination_path_nav
            }
            ref.update(data)
            ref = db.reference(f"/Patok/{index}/Storage/pos")
            data = {
                f"{label}": dropbox_destination_path_pos
            }
            ref.update(data)
            ref = db.reference(f"/Patok/{index}/Storage/post")
            data = {
                f"{label}": dropbox_destination_path_post
            }
            ref.update(data)
            ref = db.reference(f"/Patok/{index}/Realtime")
            data = {
                "time": f"{tanggal}"
            }
            ref.update(data)
            run_rnx2rtkp()
            data_status = {
                f"status": "Uploading POST Result..."
            }
            ref_status.update(data_status)
            upload_file_to_dropbox(local_file_path_pos_post, dropbox_destination_path_post,new_access_token)
            upload_data_post()
            ref = db.reference(f"/Realtime/base/")
            data = {
                f"request": 0
            }
            ref.update(data)
            time.sleep(5)
def geodetic_to_ecef(lat, lon, h, a, e2):
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    N = a / np.sqrt(1 - e2 * (np.sin(lat_rad)**2))

    x = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    z = ((1 - e2) * N + h) * np.sin(lat_rad)

    return np.array([x, y, z])
def read_last_line(file_path):
    """Read the last line of a file."""
    with open(file_path, 'rb') as file:
        file.seek(-2, 2)  # Go to the end of the file
        while file.read(1) != b'\n':  # Move backward until a newline is found
            file.seek(-2, 1)
        last_line = file.readline().decode()
    return last_line.strip()
def start_realtime():
    file_path = "/home/ronny/gnss-rover/solution.pos"
    a = 6378137.0  # Earth's semi-major axis in meters (WGS84)
    e2 = 0.00669437999014  # Earth's first eccentricity squared (WGS84)
    startup_flag = 0
    run_status_real = 0 
    while True: 
        now = datetime.now()
        minute = now.strftime("%M")
        if minute == "00" or minute == "15" or minute == "30" or minute == "45":
                run_status_real = 1
        if run_status_real == 1:
            time.sleep(10)
            last_line = read_last_line(file_path)
            ref = db.reference('Realtime')
            data = ref.child("rover").get()
            index = data['index']
            #print(index)
            if 'GPST' in last_line or '%' in last_line or len(last_line) <=2:
                time.sleep(1)
                continue
            else:
                parts = last_line.split()
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4])
                q = int(float(parts[5]))
                ns = int(float(parts[6]))
        
                # latitude, longitude, height = ecef_to_llh(x, y, z)\
                data = {
                    "lat": x,
                    "long": y,
                    "alt": z,
                    "qua": q,
                    "ns": ns
                }
                ref = db.reference("/Realtime/rover")
                ref.update(data)
                if q < 3:
                    if startup_flag == 0:
                        ref = db.reference(f"Patok/{index}/Realtime")
                        data = {
                            "lat": x,
                            "long": y,
                            "alt": z
                        }
                        ref.update(data)
                        startup_flag = 1
                    ref = db.reference(f"Patok/{index}")
                    data = ref.child("Realtime").get()
                    lat_ref = data["lat"]
                    lon_ref = data["long"]
                    h_ref = data["alt"]
                    ref_ecef = geodetic_to_ecef(lat_ref, lon_ref, h_ref, a, e2)
                    x_ref, y_ref, z_ref = ref_ecef
                    rover_ecef = geodetic_to_ecef(x, y, z, a, e2)
                    x_rover, y_rover, z_rover = rover_ecef
                    delta = np.array([x_rover - x_ref, y_rover - y_ref, z_rover - z_ref])
                    lat_ref_rad = np.radians(lat_ref)
                    lon_ref_rad = np.radians(lon_ref)
                    rot_matrix = np.array([
                        [-np.sin(lon_ref_rad), np.cos(lon_ref_rad), 0],
                        [-np.sin(lat_ref_rad) * np.cos(lon_ref_rad), -np.sin(lat_ref_rad) * np.sin(lon_ref_rad), np.cos(lat_ref_rad)],
                        [np.cos(lat_ref_rad) * np.cos(lon_ref_rad), np.cos(lat_ref_rad) * np.sin(lon_ref_rad), np.sin(lat_ref_rad)]
                    ])
                    enu = np.dot(rot_matrix, delta)
                    ref = db.reference(f"Patok/{index}/Realtime")
                    data = {
                        "east": enu[0],
                        "north": enu[1],
                        "up": enu[2]
                    }
                    ref.update(data)
                ref = db.reference(f"Patok/{index}/Realtime")
                data = {
                    "status": 1
                }
                ref.update(data)
            time.sleep(1)
def start_gui():
    # Function to update data in the grid
    # Replace this with the actual data-fetching logic
    time.sleep(15)
    def update_data():
        # Sample data for demonstration purposes
        while True:
            try:
                ref = db.reference('Realtime')
                data = ref.child("rover").get()
                if data:
                    latitude = float(data.get('lat', 0))
                    longitude = float(data.get('long', 0))
                    altitude = float(data.get('alt', 0))
                    q = int(float(data.get('qua', 0)))
                    ns = int(float(data.get('ns', 0)))
                    status      = f"{data['status']}"

                    # Data for display
                    display_data = [
                        [f"{latitude}", f"{q}"],
                        [f"{longitude}", f"{ns}"],
                        [f"{altitude}", f"{status}"]
                    ]
                    data_name = [
                        ["Latitude", "Quality"],
                        ["Longitude", "Number of Satellite"],
                        ["Altitude", "Status"]
                    ]

                    # Update the labels
                    for i in range(3):
                        for j in range(2):
                            data_labels[i][j]["name"].config(text=data_name[i][j])
                            data_labels[i][j]["value"].config(text=display_data[i][j])

                else:
                    print("No data retrieved.")
            except Exception as e:
                print(f"Error fetching data: {e}")

            # Schedule the next update
            time.sleep(1)
    # Initialize the main tkinter window
    root = tk.Tk()
    root.title("ROVER2 GPS-PPLS")
    root.geometry("480x320")  # Set resolution to match the 3.5" LCD
    root.configure(bg="black")  # Optional background color

    # Create a grid of labels with sections for name and value
    data_labels = []
    label_font = font.Font(family="Helvetica", size=14, weight="bold")
    value_font = font.Font(family="Helvetica", size=12)

    for i in range(3):
        row = []
        for j in range(2):
            frame = tk.Frame(root, bg="black", relief="ridge", bd=2)
            frame.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

            name_label = tk.Label(frame, text="", font=label_font, fg="black", bg="white", anchor="center")
            name_label.pack(fill="x", padx=5, pady=2)

            value_label = tk.Label(frame, text="", font=value_font, fg="white", bg="black", anchor="center")
            value_label.pack(fill="x", padx=5, pady=2)

            row.append({"name": name_label, "value": value_label})
        data_labels.append(row)

    # Make the grid cells expand proportionally
    for i in range(3):
        root.grid_rowconfigure(i, weight=1)
    for j in range(2):
        root.grid_columnconfigure(j, weight=1)
    threading.Thread(target=update_data, daemon=True).start()
    # update_data()
    root.mainloop()

# Main execution
if __name__ == "__main__":    
    while True:
        try:
            print("Starting Rover....")
            rinex_thread = threading.Thread(target=start_rover)
            rtkrcv_thread = threading.Thread(target=run_rtkrcv)
            realtime_thread = threading.Thread(target=start_realtime)
            gui_thread = threading.Thread(target=start_gui)
            rinex_thread.start()
            time.sleep(10)  # Allow str2str to initialize before starting rtkrcv
            rtkrcv_thread.start()
            print("Rover System Started!")
            print("Requesting to initiate Base....")
            time.sleep(5)
            realtime_thread.start()
            print("GUI Initialize....")
            time.sleep(1)
            gui_thread.start()
            rinex_thread.join()
            rtkrcv_thread.join()
            time.sleep(5)
        except Exception as e:
            print(e)
            break
