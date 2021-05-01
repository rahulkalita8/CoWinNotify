import os
import sys
import time
import logging
import requests
from datetime import datetime
from mail import Mail
from configparser import ConfigParser
from crontab import CronTab

logging.basicConfig(filename='app.log', format='%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


class CoWin:

    def __init__(self):
        self.state = None
        self.district = None
        self.pincode = None
        self.details = None
        self.base_url = "https://cdn-api.co-vin.in/api/v2/"

    def __get_vaccination_info_from_distict(self):
        dt = datetime.now()
        url = self.base_url + "appointment/sessions/calendarByDistrict?district_id={}&date={}". \
            format(self.__get_district_id(), dt.strftime('%d-%m-%Y'))
        logging.info("Hitting vaccine result by district endpoint: {}".format(url))
        response = requests.request("GET", url, verify=False)
        logging.info("Response status from district vaccine: {}".format(response.status_code))
        if response.status_code == 200:
            return response.json()
        return None

    def __get_vaccination_center_from_pincode(self):
        dt = datetime.now()
        url = self.base_url + "appointment/sessions/public/calendarByPin?pincode={}&date={}". \
            format(self.pincode, dt.strftime('%d-%m-%Y'))
        logging.info("Hitting vaccine result by pincode endpoint: {}".format(url))
        response = requests.request("GET", url, verify=False)
        logging.info("Response status from pincode vaccine: {}".format(response.status_code))
        if response.status_code == 200:
            return response.json()
        return None

    def __get_state_id(self):
        url = self.base_url + "admin/location/states"
        logging.info("Hitting all states endpoint: {}".format(url))
        response = requests.request("GET", url, verify=False)
        logging.info("Response status from states API: {}".format(response.status_code))
        if response.status_code == 200:
            states = response.json().get('states')
            for state in states:
                if state.get('state_name').lower() == self.state.lower():
                    return state['state_id']

    def __get_district_id(self):
        url = self.base_url + "admin/location/districts/{}".format(self.__get_state_id())
        logging.info("Hitting all district endpoint: {}".format(url))
        response = requests.request("GET", url, verify=False)
        logging.info("Response status from district API: {}".format(response.status_code))
        if response.status_code == 200:
            districts = response.json().get('districts')
            for district in districts:
                if district.get('district_name').lower() == self.district.lower():
                    return district['district_id']

    def send_vaccine_notification_by_mail(self, body):
        sender = config.get('mail', 'sender')
        receivers = config.get('mail', 'receivers')
        if self.district is not None:
            subject = "CoWin Vaccine Available in {}".format(self.district)
        elif self.pincode is not None:
            subject = "CoWin Vaccine Available in {}".format(self.pincode)
        else:
            subject = "CoWin Vaccine Available"
        email_client = Mail()
        email_client.connect()
        logging.info("Connected to mail client")
        email_client.send_mail(sender, receivers, subject, body)

    def get_vaccine_info(self, district=True, pincode=False):
        min_age = config.get('cowin', 'min_age') or 45
        min_capacity = config.get('cowin', 'min_capacity') or 0
        vaccine_info = ""
        vaccine_notification_body = ""
        if pincode:
            vaccine_info = self.__get_vaccination_center_from_pincode()
        elif district:
            vaccine_info = self.__get_vaccination_info_from_distict()

        if vaccine_info is not None:
            vaccine_centers = vaccine_info.get("centers", [])
            for center in vaccine_centers:
                sessions = center.get("sessions", [])
                for session in sessions:
                    if session['min_age_limit'] == int(min_age) and session['available_capacity'] > int(min_capacity):
                        vaccine_notification_body += "{} - {} - {} - Available Capacity - {}\n". \
                            format(center.get('pincode'), center.get('name'), session.get('date'),
                                   session.get('available_capacity'))

        logging.info("Number of possible vaccination point found: {}".format(str(len(vaccine_notification_body))))

        if len(vaccine_notification_body) > 0:
            self.send_vaccine_notification_by_mail(vaccine_notification_body)

    def add_crontab(self, pincode=False):
        logging.info("Adding cron job")
        if enable_cron:
            freq = config.get('cron', 'freq') or "10"
            freq = int(freq)
            username = config.get('cron', 'username') or "rkalita"
            cron_client = CronTab(user=username)
            python_file_path = os.path.abspath(__file__)
            if pincode:
                job = "python {} {}".format(python_file_path, self.pincode)
            else:
                job = "python {} {} {}".format(python_file_path, self.state, self.district)
            cron_job = cron_client.new(job)
            cron_job.minute.every(freq)
            cron_client.write()


if __name__ == '__main__':
    pwd = os.getcwd()
    config = ConfigParser()
    config_path = os.path.dirname(os.path.abspath(__file__))
    config.read_file(open(os.path.join(config_path, '../resources/configuration.ini')))
    enable_cron = config.get('cron', 'enable') or "false"
    freq = config.get('cron', 'freq') or "10"
    freq = int(freq)
    cowin = CoWin()
    args_len = len(sys.argv)
    args = sys.argv
    logging.info("Argument received: {}".format(str(args)))
    if args_len == 2:
        cowin.pincode = args[1]
        # if enable_cron.lower() == "true":
        #     cowin.add_crontab(pincode=True)
        # else:
        while True:
            cowin.get_vaccine_info(district=False, pincode=True)
            time.sleep(60*freq)
    if args_len == 3:
        cowin.state = args[1]
        cowin.district = args[2]
        # if enable_cron.lower() == "true":
        #     cowin.add_crontab()
        # else:
        while True:
            cowin.get_vaccine_info()
            time.sleep(60*freq)
