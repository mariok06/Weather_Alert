import requests
import smtplib
import os

# Constants
API_KEY = os.environ.get('API_KEY')
COUNTRY_CODE = 'IND'
PASS_KEY = os.environ.get('PASS_KEY')
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
FROM = os.environ.get('FROM')
emojis_list = ['⛈️', '🌧️', '🌦️', '❄️', '🌫️', '☀️', '🌙', '🌥️', '🌃', '☁️', '🌃☁️', '☁️', '🌙☁️']
emoji_num = ['11d', '09d', '10d', '13d', '50n', '01d', '01n', '02d', '02n', '03d', '03n', '04d', '04n']


class Emails:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0

    def get_geocodes(self, city):
        response_two = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city},{COUNTRY_CODE}&appid={API_KEY}')
        geocode_data = response_two.json()
        print(geocode_data)
        self.latitude = geocode_data[0]['lat']
        self.longitude = geocode_data[0]['lon']
        weather_params = {
            'lat': self.latitude,
            'lon': self.longitude,
            'appid': API_KEY,
        }
        return weather_params

    def send_emails(self, email, params):
        # Requests weather data
        response_one = requests.get(url=WEATHER_API_URL, params=params)
        weather_data = response_one.json()

        # Sorts weather data received.
        weather = weather_data['weather'][0]['main']
        condition_code = weather_data['weather'][0]['id']
        t_max = round(weather_data['main']['temp_max'])
        temp = [i for i in str(t_max)]
        max_temp = temp[0] + temp[2]
        print(weather_data)

        # Gets weather emoticon for specific weather.
        icon = weather_data['weather'][0]['icon']
        emoji = ''
        for num in emoji_num:
            if num == icon:
                emoji = emojis_list[emoji_num.index(icon)]

        # Email messages
        might_rain_msg = f"Subject: {weather} {emoji} \nToday's Temperature hits {max_temp}°C! \nIt might rain today! \nCarry an umbrella with you 🌂"
        will_rain_msg = f"Subject: {weather} {emoji} \nToday's Temperature hits {max_temp}°C! \nDon't forget to carry an umbrella with you ☔ \nAnd be aware of the mud holes while traveling 🚗"
        thunderstorm_msg = f"Subject: {weather} {emoji} \nToday's Temperature hits {max_temp}°C! \nBe aware of those lightning strikes. \nTake Care 💗"
        heatwaves_msg = f"Subject: {weather} {emoji} \nSevere Heatwaves Alert! \nToday's Temperature hits {max_temp}°C! \nDon't step out of your house between 10 AM to 2 PM."
        normal_msg = f"Subject: {weather} {emoji} \nToday's Temperature hits {max_temp}°C! \nPerfect weather to befriend a cat 🐈"

        # Sets weather messages as per condition codes received.
        might_rain = False
        will_rain = False
        thunderstorm = False
        heatwaves = False
        normal = False

        if 200 < condition_code < 240:
            thunderstorm = True
        elif 300 < condition_code < 330:
            might_rain = True
        elif 500 < condition_code < 540:
            will_rain = True
        elif 700 < condition_code < 790:
            heatwaves = True
        elif 790 < condition_code < 805:
            normal = True

        with smtplib.SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(user=FROM, password=PASS_KEY)
            if thunderstorm:
                connection.sendmail(from_addr=FROM, to_addrs=email,
                                    msg=thunderstorm_msg.encode('utf-8'))
            elif might_rain:
                connection.sendmail(from_addr=FROM, to_addrs=email,
                                    msg=might_rain_msg.encode('utf-8'))
            elif will_rain:
                connection.sendmail(from_addr=FROM, to_addrs=email,
                                    msg=will_rain_msg.encode('utf-8'))
            elif heatwaves:
                connection.sendmail(from_addr=FROM, to_addrs=email,
                                    msg=heatwaves_msg.encode('utf-8'))
            elif normal:
                connection.sendmail(from_addr=FROM, to_addrs=email,
                                    msg=normal_msg.encode('utf-8'))
