from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import pandas as pd
import streamlit as st
import pickle
from deep_translator import GoogleTranslator
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import json







# Set headless mode (optional)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)





def  get_train_data():

    dic = {"General":"GN","Tatkal":"TQ","Ladies":"LD","Lower berth":"LB","Premium tatkal":"PT","Defence quota": "DF","Divyangan(Physically handicaped)":"HP","Foreign Tourist quota":"FT","Yuva":"YU","Duty pass":"DP","Parliament house quota":"PH"}  

    with open("station_codes.pkl", 'rb') as file:
        stations = pickle.load(file)

    key = list(stations.keys())
    val = list(stations.values())

    stat = []
    for i in range(len(key)):
        key[i] = key[i].replace(" ","-")
        res = (key[i]+"-"+val[i]).lower()
        stat.append(res)
    
    # Load the animation outside the Streamlit loop and cache it
    @st.cache_data(ttl=60 * 60)
    def load_lottie_file(filepath : str):
        with open(filepath, "r") as f:
            gif = json.load(f)
        return gif

    gif = load_lottie_file("train_avail.json")

    # Display the animation with a placeholder image while loading
    with st.spinner("Loading animation..."):
        st_lottie(gif, speed=1, width=650, height=250)

    st.markdown("<h1 style='text-align: center; color: #008080;'><u>Check the train availability</u></h1>", unsafe_allow_html=True)
    st.markdown("""---""")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        From = st.selectbox("🚇 "+"From: ",stat)

    with col2:
        To = st.selectbox("🚇 "+"To: ",stat) 

    with col3:
        D = st.date_input("🗓️ "+"Select travel date: ")
        Date = D.strftime("%d-%m-%Y")
    with col4:
        quota = st.selectbox("🚇 "+"select the quota type : ",list(dic.keys()))
    try:
        url = f"https://www.trainman.in/trains/{From}/{To}?date={Date}&class=ALL&quota={quota}"
    except:
        st.error("Sorry trains data unavailable")

    try:
        driver.get(url)
    except:
        st.error("Sorry trains data unavailable")

    D3 = []
    train_number = driver.find_elements(By.CSS_SELECTOR, "span[class='tcode f-poppins-semibold']")
    train_name = driver.find_elements(By.CSS_SELECTOR,"span[class='short-train-name f-poppins-medium t-ellipsis']")

    elements = driver.find_elements(By.CSS_SELECTOR,"div[class='info-schedule-container']")

    for i in elements:
        D3.append(i.text)

    # print(D3)

    train_number_with_name = []
    Days = []
    for i in D3:
        r3 = i.replace("\n"," - ")
        train_number = r3.split(" - ")[0]+" - "+r3.split(" - ")[1]
        train_number_with_name.append(train_number)

    # print(train_number_with_name)

    running_days_containers = driver.find_elements(By.CSS_SELECTOR, "div[class='running-days t-primary-400']")
    all_running_days = []

    for container in running_days_containers:
        running_days = container.find_elements(By.CSS_SELECTOR, "span[class='run-day t-accent-500 ng-star-inserted']")
        container_running_days = []
        for day in running_days:
            container_running_days.append(day.text)
        if container_running_days == ["M","T","W","T","F","S","S"]:
            all_running_days.append("Runs daily")
        else:
            days = container_running_days.copy()
            if "T" in days:
                idx = days.index("T")
                days[idx] = "Tue"
            if "S" in days:
                days[days.index("S")] = "Sat"
            if "M" in days:
                days[days.index("M")] = "Mon"
            if "W" in days:
                days[days.index("W")] = "Wed"
            if "F" in days:
                days[days.index("F")] = "Fri"

            all_running_days.append(",".join(days))

    # print(all_running_days)
        
    

    # for i in elements:
    #     print(i.text)
    D1 = []
    D2 = []
    available = []
    div = driver.find_elements(By.CSS_SELECTOR,"div[class='time d-flex-row-jc-sb w-100']")
    route = driver.find_elements(By.CSS_SELECTOR,"div[class='route']")
    avail = driver.find_elements(By.CSS_SELECTOR,"div[class='future-avl-card b-primary-350-full t-primary-500 c-pointer']>a")

    for i in div:
        D1.append(i.text)

    for i in route:
        D2.append(i.text)

    for i in avail:
        available.append(i.get_attribute("href"))

    timings = []
    route = []
    for i in D1:
        r = i.replace("\n"," - ")
        timings.append(r)

    for i in D2:
        r1 = i.replace("\nView route\n"," to ")
        route.append(r1)
    # print(timings)
    # print(route)

    df2 = pd.DataFrame({"Train_name":train_number_with_name,"Timings":timings,"Route":route,"Seats availability":available,"Running_days":all_running_days})
    # st.dataframe(df2)

    df2.to_csv("train_stations.csv",index=False)

    D = {}
    for index,row in df2.iterrows():
        key = row["Train_name"]
        value = row["Seats availability"]
        D[key] = value

    with open("train_seat_availability.pkl","wb") as file:
        file.write(pickle.dumps(D))
    
    

    # Iterate over the train information
    
    with open("languages.pkl","rb") as file:
        languages = pickle.load(file)

    lang = st.selectbox("select the language to translate: ",list(languages.keys()))

    source_language = "en"
    target_language = languages[lang]

    if all([len(train_number_with_name),len(timings),len(route)]) != 0:
        for i in range(len(train_number_with_name)):
            note = "**Note**: In Running days T = Thursday and S = Sunday"
            translated_note = GoogleTranslator(source=source_language, target=target_language).translate(note)
            st.warning(translated_note)
            with st.container():
                # Translate and display the note
                

                st.markdown("---")
                st.markdown(
                    f"<h2 style='color: green;'>🚉 Train Name: {train_number_with_name[i]}</h2>",
                    unsafe_allow_html=True
                )
                
                # Conditionally translate only if the data is a string
                # Labels to be translated
                labels = {
                    "Timings": timings[i],
                    "Route": route[i],
                    "Running Days": all_running_days[i]
                }

                # Translate labels and values
                translated_labels = {}
                for key, value in labels.items():
                    if isinstance(value, str):
                        translated_labels[key] = GoogleTranslator(source=source_language, target=target_language).translate(key)
                        translated_value = GoogleTranslator(source=source_language, target=target_language).translate(value)
                    else:
                        translated_labels[key] = key
                        translated_value = value
                    
                    labels[key] = translated_value

                # Display translated labels and values
                for key, value in labels.items():
                    st.subheader(f":blue[{translated_labels[key]}]: :orange[{value}]")

                st.markdown("---")
    else:
        st.warning("Sorry trains data unavailable")
    
            




def train_route():
    df1 = pd.read_csv("train_info.csv")

    # inserting JSON image
    container = st.container()
    try:
        with container:
            @st.cache_data(ttl=60 * 60)
            def load_lottie_file(filepath : str):
                with open(filepath, "r") as f:
                    gif = json.load(f)
                st_lottie(gif, speed=1, width=650, height=250)
                
            load_lottie_file("train_route.json")
    except:
        print("Don't raise exception")

    st.title("finding train routes to get the station details")
    st.warning("**Note**: some train numbers data are not there in database in that case you will get empty dataframe")
    
    dataF = pd.read_csv("train_stations.csv")


    option = st.radio("Choose input method:", ("Text Input", "Select Box"))

    if option == "Text Input":
        selected_train = st.text_input("Enter your destination train number:")
    elif option == "Select Box":
        train_list = list(dataF["Train_name"])
        selected_train = st.selectbox("Select your destination train number:", train_list)
        selected_train = selected_train.split("-")[0]
            

    but = st.button("click here to fetch the results")
    
    df1["train_number"].replace(",","",inplace=True)
    with st.sidebar:
        # Display a message or summary of the DataFrame
        st.write("**Train Details**")
        st.dataframe(df1)  # Show first 2 rows



    
    data = []
    try:
        url = f"https://www.trainman.in/train/{selected_train}"
        driver.get(url)
    except:
        print("don't raise web drive exception")
    train_route = driver.find_elements(By.CSS_SELECTOR,"tr[class='ng-star-inserted']")
    for i in train_route:
        data.append(i.text.split())

    S_no = []
    station = []
    Arr_dep_time = []
    halt_stop_min = []
    day = []
    distance = []
    platform = []
    for row in data:
        if len(row) == 14 and "Starts" in row:
            S_no.append(row[0])
            station_name = " ".join(row[1:row.index("(")]) if "(" in row else "-"
            station.append(station_name + " " + "".join(row[row.index("("):row.index(")") + 1]) if "(" in row else "-")
            Arr_dep = " ".join(row[row.index("Starts"):row.index("Starts") + 2]) if "Starts" in row else "-"
            Arr_dep_time.append(Arr_dep)
            halt_stop = row[row.index("Starts") + 2] if "Starts" in row else "-"
            halt_stop_min.append(halt_stop)
            day_value = row[row.index("Starts") + 3] if "Starts" in row else "-"
            day.append(day_value)
            distance_val = row[row.index("Starts") + 4] + " " + row[row.index("Starts") + 5] if "Starts" in row else "-"
            distance.append(distance_val)
            platform_val = row[-1] if row[-1] else "-"
            platform.append(platform_val)
        elif "Ends" not in row:
            S_no.append(row[0])
            station_name = " ".join(row[1:row.index("(")]) if "(" in row else "-"
            station.append(station_name + " " + "".join(row[row.index("("):row.index(")") + 1]) if "(" in row else "-")
            Arr_dep = "".join(row[row.index(")") + 1] + " to " + row[row.index(")") + 2]) if ")" in row else "-"
            Arr_dep_time.append(Arr_dep)
            halt_stop = row[row.index(")") + 3] + " " + row[row.index(")") + 4] if ")" in row else "-"
            halt_stop_min.append(halt_stop)
            day_value = row[row.index(")") + 5] if ")" in row else "-"
            day.append(day_value)
            distance_val = row[row.index(")") + 6] + " " + row[row.index(")") + 7] if ")" in row and len(row) > row.index(")") + 7 else "-"
            distance.append(distance_val)
            platform_val = row[-1] if row[-1] else "-"
            platform.append(platform_val)
        else:
            S_no.append(row[0])
            station_name = " ".join(row[1:row.index("(")]) if "(" in row else "-"
            station.append(station_name + " " + "".join(row[row.index("("):row.index(")") + 1]) if "(" in row else "-")
            Arr_dep = "".join(row[row.index(")") + 1] + " to " + row[row.index(")") + 2]) if ")" in row else "-"
            Arr_dep_time.append(Arr_dep)
            halt_stop = row[row.index(")") + 3] if ")" in row else "-"
            halt_stop_min.append(halt_stop)
            day_value = row[row.index(")") + 4] if ")" in row else "-"
            day.append(day_value)
            distance_val = row[row.index(")") + 5] + " " + row[row.index(")") + 6] if ")" in row else "-"
            distance.append(distance_val)
            platform_val = row[-1] if row[-1] else "-"
            platform.append(platform_val)


    # print(S_no)
    # print(station)
    # print(Arr_dep_time)
    # print(halt_stop_min)
    # print(day)
    # print(distance)
    # print(platform)


    data = {
        "S_no":S_no,
        "Station":station,
        "Arrival/Departed time":Arr_dep_time,
        "Halt/Stop (mins)":halt_stop_min,
        "day":day,
        "Distance (km)":distance,
        "Platform":platform
    }


    if but and data is not None:
        df = pd.DataFrame(data)
        df["Platform"].replace("km","-",inplace=True)
        st.dataframe(df)

   
def seat_availability():
    st.image("seat.gif",use_column_width=True)
    st.title("Check the train seat availability")
    dataF = pd.read_csv("train_stations.csv")
    st.warning("**Note**: **check** means the data not updated yet")
    option = st.radio("Choose input method:", ("Text Input", "Select Box"))

    if option == "Text Input":
        train_no = st.text_input("Enter your destination train number:")
        seat_avail = f"https://www.trainman.in/seat-availability/{train_no}"
    elif option == "Select Box":
        D = {}
        for index, row in dataF.iterrows():
            key = row["Train_name"]
            value = row["Seats availability"]
            D[key] = value

        train_list = list(D.keys())
        sel = st.selectbox("Select your destination train number:", train_list)
        seat_avail = D[sel]

    but = st.button("Click here to get the seat availability status")

    if but:
        try:
            # Set headless mode (optional)
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)

            driver.get(seat_avail)
            # Find all th elements to extract column headings
            columns = driver.find_elements(By.CSS_SELECTOR, "table[class='table text-center table-bordered ng-star-inserted'] th")
            column_names = [col.text for col in columns]

            # Find all tr elements to extract table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "table[class='table text-center table-bordered ng-star-inserted'] tr")
            data = []

            # Iterate over the rows to populate the data
            for row in rows[1:]:  # Start from index 1 to skip the header row
                row_data = [td.text for td in row.find_elements(By.TAG_NAME, "td")]
                data.append(row_data)

            # Close the webdriver to release resources
            driver.quit()

            # Create a DataFrame using the extracted column headings and data
            df = pd.DataFrame(data, columns=column_names)

            # Display the DataFrame
            st.dataframe(df)

        except:
            st.error("Failed to fetch seat availability. Please try again later.")
    
    
def PNR_Status():
    st.image("pnr.gif",use_column_width=True)
    st.title("Check the PNR status of your booking")
    pnr = st.text_input("Enter PNR:", value="1234567890")
    if st.button("Get Details"):
        try:
            response = requests.get(f"https://api.website.com/pnr/{pnr}")
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
            json_data = response.json()

            if st.button("Get Details"):
                st.markdown(f"<span style='color: blue'><b>PNR:</b> {json_data['pnr']}</span>", unsafe_allow_html=True)
                st.subheader("Train Details:")
                journey_details = json_data['journeyDetails']
                for key, value in journey_details.items():
                    st.write(f"- <span style='color: green'><b>{key.capitalize()}:</b></span> {value}")

                st.write(f"- <span style='color: green'><b>Last Updated:</b></span> {json_data['lastUpdated']}")

                st.subheader("Booking Status:")
                booking_status = json_data['bookingStatus']
                for passenger in booking_status:
                    st.write(f"<span style='color: red'>Passenger {passenger['passengerNo']}:</span>")
                    st.write(f"  - <span style='color: purple'><b>Booking Status:</b></span> {passenger['bookingStatus']}")
                    st.write(f"  - <span style='color: purple'><b>Current Status:</b></span> {passenger['currentStatus']}")

                st.write(f"<span style='color: blue'><b>Charting Status:</b></span> {json_data['chartingStatus']}")
        except Exception as e:
            st.error("Failed to fetch data. Please try again later.")




menu_options = {
    "🚂 Finding Trains": "finding trains",
    "🚊 Train Route": "train route",
    "💺 Seats Availability": "Seats_availability",
    "🆔 PNR Status": "PNR Status"
}

selected = option_menu("", list(menu_options.keys()), orientation="horizontal")

page_functions = {
    "finding trains": get_train_data,
    "train route": train_route,
    "Seats_availability": seat_availability,
    "PNR Status": PNR_Status
}
page_functions[menu_options[selected]]()
