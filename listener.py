import json
import time

import ac
import webhook_listener


def process_post_request(request, *args, **kwargs):
    body = request.body.read().decode("utf-8")
    json_body = json.loads(body)

    conversation_url = json_body['_links']['web']['href']
    email = json_body['primaryCustomer']['email']
    raw_thread = json_body['_embedded']['threads']

    thread = {}
    messages = []

    for msg in raw_thread:
        if msg['type'] != 'lineitem' and 'Technical Information' not in msg['body']:
            message = msg['body']
            firstname = msg['createdBy']['first']
            lastname = msg['createdBy']['last']
            temp = {}
            temp['message'] = message
            temp['sender'] = '{} {}'.format(firstname, lastname)
            temp['date'] = msg['createdAt']
            temp['type'] = msg['createdBy']['type']
            messages.append(temp)

    thread['messages'] = messages
    thread['url'] = conversation_url

    contact_id = ac.get_contact_id(email)
    ac.add_note(thread, contact_id)
    
    return '200 OK'


webhooks = webhook_listener.Listener(
    handlers={"POST": process_post_request},
    host='',
)
webhooks.start()

while True:
    print("Still alive...")
    time.sleep(300)
