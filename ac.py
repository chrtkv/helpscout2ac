import json

from requests import request

from bs4 import BeautifulSoup

with open('config.json') as config:
    CONFIG = json.load(config)

URL = CONFIG['api_url']
KEY = CONFIG['api_key']

def formatter(thread):
    result = '{}\n\n'.format(thread['url'])
    for message in reversed(thread['messages']):
        if message['type'] == 'user':
            line = '---------------------------------------------'
        if message['type'] == 'customer':
            line = '****************************************'
        if message['type'] == 'note':
            line = '////////////////////////////////////////'
        result += (
            line
            + '\n'
            + message['sender'] + '\t' + message['date']
            + '\n'
            + '\n'.join(filter(None, BeautifulSoup(message['message']).get_text('\n').splitlines()))
            + '\n'
            + '\n'
        )

    return result


def update_note(note, note_id, contact_id):
    url = "{}/notes/{}".format(URL, note_id)

    payload = {
        'note': {
            'note': note,
            'relid': contact_id,
            'reltype': 'Subscriber'
        }
    }

    headers = {
        'api-token': KEY,
        'content-type': "application/json",
    }

    return request("PUT", url, json=payload, headers=headers)


def add_note(note, contact_id):
    note_text = formatter(note)
    contact_notes = get_contact_notes(contact_id)
    note_id = ''

    for note_item in contact_notes:
        conversation_url = note_item['note'].split('\n')[0]
        new_conversatioin_url = note_text.split('\n')[0]
        if new_conversatioin_url == conversation_url:
            note_id = note_item['id']
            return update_note(note_text, note_id, contact_id)

    url = "{}/notes".format(URL)

    payload = {
        'note': {
            'note': note_text,
            'owner': contact_id,
            'reltype': 'Subscriber'
        }
    }

    headers = {
        'api-token': KEY,
        'content-type': "application/json",
    }

    return request("POST", url, json=payload, headers=headers)


def get_contact_id(email):
    url = '{}/contacts'.format(URL)
    querystring = {'search': email}
    headers = {'api-token': KEY}
    response = request('GET', url, headers=headers, params=querystring)

    return response.json()['contacts'][0]['id']


def get_contact_notes(contact_id):
    url = '{}/contacts/{}/notes'.format(URL, contact_id)
    headers = {'api-token': KEY}
    response = request('GET', url, headers=headers)
    notes = response.json()['notes']

    return notes


def remove_note(note_id):
    url = "{}/notes/{}".format(URL, note_id)
    headers = {'api-token': KEY}

    return request("DELETE", url, headers=headers)


def clear_notes(contact_id):
    notes = get_contact_notes(contact_id)
    for note in notes:
        remove_note(note['id'])
