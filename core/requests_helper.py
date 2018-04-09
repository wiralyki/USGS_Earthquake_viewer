
import requests

class RequestsData(object):

    def __init__(self, urls):

        self._urls = urls

    def run(self):

        results = [
            self.retrying(url)
            for url in self._urls
        ]

        output = {}
        for data in results:
            output.update(data.json())

        return output

    def retrying(self, url):

        retrying = True
        while retrying:
            response = requests.get(url)
            if response.status_code == 200:
                retrying = False
        return response