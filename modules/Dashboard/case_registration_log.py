from flask import Flask, request, jsonify, Blueprint
import json
from datetime import datetime
import requests

# from utils import send_email_with_excel


bp = Blueprint('case_registration_log', __name__)


def case_registration_log_blueprint(_db, _app,  _log):
    global db
    global app
    global log
    log = _log
    app = _app
    db = _db
    return bp


@bp.route('/api/dashboard/allClientCaseLog', methods=['POST'])
def case_log():
    try:
        # data = {}
        # print("request.json",request.json)
        data = request.json or {}

        if data != {}:
            if ('fromDate' in data and 'toDate' in data) and (data['fromDate'] and data['toDate']):
                fromDate = data['fromDate']
                toDate = data['toDate']
                date_input = f'from_date={fromDate}&to_date={toDate}'

            elif ('fromDate' in data) and data['fromDate'] :
                fromDate = data['fromDate']
                toDate = datetime.now().strftime('%d-%m-%Y')
                date_input = f'from_date={fromDate}&to_date={toDate}'

            elif ('toDate' in data) and data['toDate']:
                toDate = data['toDate']
                date_input = f'to_date={toDate}'

        else:
            toDate = datetime.now().strftime('%d-%m-%Y')
            date_input = f'to_date={toDate}'
        
        url = f"https://testapiintegration.matex.co.in/dash/v1/api/getStat?statType=Case%20Registration%20Automation&{date_input}"
        response = requests.request("GET", url, headers={}, data={})

        return jsonify({'success':True, 'message':'Success', 'description' : response.json()['data']}), 200

    except Exception as e:
        return jsonify({'success':False, 'message':'Not success', 'description' : str(e)}), 200
    


# @bp.route('/api/dashboard/caseLogMail', methods=['POST'])
# def send_case_log_mail():
#     try:
#         send_email_with_excel(
#             subject="Test Subject",
#             body="This is a test email with an Excel attachment.",
#             email_config=email_config,
#             json_data=json_data
#         )
    
#     except Exception as e:
#         raise e