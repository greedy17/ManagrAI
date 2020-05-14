# this is a temp server file used to mimic redirect from front end until it is built
# it is served by flask
import requests
from flask import Flask, request
app = Flask(__name__)


@app.route('/api/connect-email')
def send_code():
    code = request.args.get('code', None)
    # state is the magic token we passed to Nylas
    state = request.args.get('state', None)
    client = requests.Session()
    res = client.post('http://localhost:8000/api/users/email-auth-token/',
                      headers={
                          'Authorization': 'token f5cbb7185985856abc81c7a1e92b647ae6bd6baf'},
                      data={'magic_token': state, 'code': code})

    if res.status_code >= 200 and res.status_code <= 400:
        return res.json()

    return "Generate Token"


if __name__ == '__main__':
    app.run(debug=True)
