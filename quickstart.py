from __future__ import print_function
import datetime
import pickle
import os.path
import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#converts a string in to a datetime object
def convert_str_to_datetime(date_info):
    datetime_obj = datetime.datetime.strptime(date_info, '%Y-%m-%dT%H:%M:%S%z')
    return datetime_obj

#checks to make sure the string is formatted correctly to ignore full day events without times
def is_valid_date_time_string(datetimestring):
    try:
        datetime.datetime.strptime(datetimestring, '%Y-%m-%dT%H:%M:%S%z')
        is_valid = True
    except ValueError:
        is_valid = False
    return is_valid

#converts a datetime object in to a date string "Monday, February 3"
def convert_datetime_to_date(date_info):
    return date_info.strftime("%A, %B %d")

#converts a datetime object in to a time string 4:15 PM"

def convert_datetime_to_time(date_info):
    return date_info.strftime("%I:%M %p")

def prettify_event(event):
    date = convert_datetime_to_date(event["start_time"])
    start_time_formatted = convert_datetime_to_time(event["start_time"])
    end_time_formatted = convert_datetime_to_time(event["end_time"])
    open_slot_formatted = {"date": date, "start_time": start_time_formatted, "end_time": end_time_formatted}
    return open_slot_formatted

def check_if_valid(event):
    if (event['duration'].seconds > 900) and (event['duration'].seconds < 28800):
        return True
    return False

def display_formatted_list(events_dict):
    for event in events_dict:
        print(f'{event["date"]}, {event["start_time"]} - {event["end_time"]}')

# Ensure that available spots don't go across days
# Set a Max duration (8 hours?) - DONE
# Set a minimum duration - DONE


# datetime_obj = datetime.datetime.now()
# print(datetime_obj)
# print(convert_datetime_to_date(datetime_obj), convert_datetime_to_time(datetime_obj) )

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # print(now)
    print("Looking for your free appointment times...")
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=40, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    open_times = []
    pp = pprint.PrettyPrinter(depth=6)
    # pp.pprint(events[0])
    if not events:
        print('No upcoming events found.')
    for i in range(len(events)-1):
        # start = events[i]['start'].get('dateTime', events[i]['start'].get('date'))
        if is_valid_date_time_string(events[i]['end'].get('dateTime', events[i]['end'].get('date'))) and is_valid_date_time_string(events[i+1]['start'].get('dateTime', events[i+1]['start'].get('date'))):
            end = convert_str_to_datetime(events[i]['end'].get('dateTime', events[i]['end'].get('date')))
            start_of_next = convert_str_to_datetime(events[i+1]['start'].get('dateTime', events[i+1]['start'].get('date')))

            # print(start, events[i]['summary'])
            duration = start_of_next - end
            open_slot = {"start_time": end,"end_time": start_of_next, "duration": duration}
            open_slot_formatted = prettify_event(open_slot)
            if check_if_valid(open_slot):
                open_times.append(open_slot_formatted)

    display_formatted_list(open_times)



if __name__ == '__main__':
    main()

# To do:
# Ensure that available spots don't go across days
# Set a Max duration (8 hours?)
# Set a minimum duration
#ignore full day events? Or only full day events where status is free?
