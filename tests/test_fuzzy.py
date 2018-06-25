import random
from app.runtime import execute_notebook
from app.model import Field, build_form_fields

context = { 'filename': 'primary' }
success = 0

def test_main():
    fields = build_form_fields()
    try:
        for k, v in fields.items():
            fields[k].value = random.choice(fields[k].choices())
        execute_notebook(thread_yield, thread_stopper, app, context)
        success += 1
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(e)
        assert False
