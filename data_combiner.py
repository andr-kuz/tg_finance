import json
import re


fname = 'main.beancount'
number_contained_messages = {}

with open(fname, 'r') as f:
    data = json.load(f)

date = beancount_content = ''
regexp = re.compile(r'(?:^|\n)[-\+]?\d+\.?\d* ')

for msg in data['messages'][:]:  # iterating a copy
    text = msg['text']
    numbers = re.findall(regexp, text) if isinstance(text, str) else []
    if (
        not text 
        or (
            not numbers
            and not msg.get('reply_to_message_id') in number_contained_messages
        )
    ):
        data['messages'].remove(msg)
        continue
    dt = msg['date'][:10]
    if dt != date:
        date = dt
        beancount_content += f'{date} *\n'
    commentaries = [result for result in re.split(regexp, text) if result]
    for i, commentary in enumerate(commentaries):
        commentary = commentary.strip()
        beancount_content += '  '
        try:
            beancount_content += f'{numbers[i].strip()} RUB ; {commentary}'
        except IndexError:
            reply_id = msg.get('reply_to_message_id')
            if reply_id:
                related_message = number_contained_messages[reply_id]
                beancount_content += f'; {commentary} -- {related_message["text"]}'
            else:
                break
        beancount_content += '\n'

    number_contained_messages[msg['id']] = msg


with open('bean.beancount', 'w') as f:
   f.write(beancount_content) 

ids = [str(id) for id in number_contained_messages.keys()]
with open('messages_to_remove.txt', 'w') as f:
   f.write(';'.join(ids)) 
