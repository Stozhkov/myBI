from app import db, celery
from celery.app.control import Inspect


def check_tasks():
    i = Inspect(app=celery)
    tasks_dict = i.active()

    if tasks_dict:
        keys = list(tasks_dict)
        tasks_list = tasks_dict[keys[0]]
        tasks_result = []
        for task in tasks_list:
            tasks_result.append({
                'id': task['id'],
                'start_date': task['args'][0],
                'end_date': task['args'][1]
            })

        return tasks_result
    else:
        return False

