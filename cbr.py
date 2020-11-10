import bs4
import requests


class CBR:
    def __init__(self):
        self.url = 'http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx'

    @staticmethod
    def __convert_to_list(xml_data, date):
        all_data = []

        soup = bs4.BeautifulSoup(xml_data, 'xml')
        rows = soup.find_all('ValuteCursOnDate')

        if rows is not []:

            for row in rows:
                data = {'Vname': row.find('Vname').get_text().strip(),
                        'Vnom': row.find('Vnom').get_text(),
                        'Vcurs': row.find('Vcurs').get_text(),
                        'Vcode': row.find('Vcode').get_text(),
                        'VchCode': row.find('VchCode').get_text()
                        }
                all_data.append(data)

            return {'date': date, 'curs': all_data}
        else:
            return False

    def get_curs_on_date(self, date):

        body = """<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <GetCursOnDate xmlns="http://web.cbr.ru/">
                      <On_date>""" + date + """</On_date>
                    </GetCursOnDate>
                  </soap:Body>
                </soap:Envelope>"""

        body = body.encode('utf-8')

        try:
            session = requests.session()
            session.headers = {"Content-Type": "text/xml; charset=utf-8"}
            session.headers.update({"Content-Length": str(len(body))})
            response = session.post(url=self.url, data=body, verify=False)
        except Exception as e:
            print(e)
            return False
        else:
            return CBR.__convert_to_list(response.text, date)
