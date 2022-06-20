from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
import os
import email
import base64
import datetime
import html2text
import time


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
	"""Shows basic usage of the Gmail API.
	Lists the user's Gmail labels.
	"""
	creds = None
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('gmail', 'v1', credentials=creds)

	return service
# returns service


def search_messages(service, user_id, search_string):
	try:
		search_id = service.users().messages().list(userId=user_id, q=search_string).execute()
		number_of_results = search_id['resultSizeEstimate']
		final_messageIDlist=[]
		if number_of_results > 0:
			for ids in search_id['messages']:
				final_messageIDlist.append(ids['id'])
			return final_messageIDlist
		else:
			print("No mails match the query.")
			return ''
	except:
		print('An error occured.')
# returns final list of message IDs


def get_message(service, user_id, msg_id):
	try:
		message_list = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
		msg_raw = base64.urlsafe_b64decode(message_list['raw'].encode('ASCII'))
		msg_string = email.message_from_bytes(msg_raw)
		if msg_string['Subject'].lower() == 'youtube':
			message_body = msg_string.get_payload()[0].get_payload()
			return message_body
		else:
			print("Nothing to see there lol")
	except:
		print('There was an error.')
# returns the final contents of the message


def downloader(message_body):
	link_list = message_body.split("\n")
	for linkofit in link_list:
		if len(linkofit.split(" ")) == 2:
			type, link = linkofit.split(" ")
			try:
				if type.lower() == 'm':
					os.system(f"""/usr/bin/python3 /usr/local/bin/youtube-dl -o "~/Desktop/ytdls/%(title)s.%(ext)s" '{link}' -x --audio-format mp3 {link}""")
				elif type.lower() == 'v':
					os.system(f"""/usr/bin/python3 /usr/local/bin/youtube-dl -o "~/Desktop/ytdls/%(title)s.%(ext)s" '{link}' -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4' {link}""")
				print("\n")
			except:
				print("That line didn't have a link lol continuing\n")
		else:
			continue
# takes single string in form "{format} {link}" and downloads it


def loop(interval, count):
	if count > 0:
		body()
		for turn in range(count-1):
			time.sleep(interval)
			body()
		print("")
# pretty self explanatory

def body():
	search_string='is:unread in:inbox subject:youtube'
	user_id='me'
	service = get_service()
	for msg_id in search_messages(service, user_id, search_string):
		message_body=get_message(service, user_id, msg_id)
		downloader(message_body)
# main downloader command line that uses every other def^


response = input("Loop? (Y/N): ").lower()

if response == 'y':
	interval = float(input("Interval(s): "))
	count = int(input("Count: "))
	print("")
	loop(interval, count)

elif response == 'n':
	body()

else:
	print("Please try again.")
