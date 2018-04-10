import random
from app.runtime import execute_notebook
from app.model import Field, fields

context = { 'filename': 'primary' }
success = 0

while True:
    try:
        for k, v in fields.items():
            fields[k].value = random.choice(fields[k].choices())
        execute_notebook(thread_yield, thread_stopper, app, context)
        success += 1
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
        break
