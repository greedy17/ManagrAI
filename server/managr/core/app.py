# this is a temp server file used to mimic redirect from front end until it is built
# it is served by flask
import requests
from flask import Flask, request, redirect

app = Flask(__name__)


@app.route('/api/connect-email')
def send_code():
    code = request.args.get('code', None)
    # state is the magic token we passed to Nylas
    state = request.args.get('state', None)
    client = requests.Session()
    res = client.post(
        'http://localhost:8000/api/users/email-auth-token/',
        headers={'Authorization': 'token b517988dd772b7d816a0f79bf89e3ec4c405c2d5'},
        data={'magic_token': state, 'code': code},
    )

    if res.status_code == 204:
        return redirect("http://localhost:8080/settings", code=302)

    return "Generate Token"


if __name__ == '__main__':
    app.run(debug=True)
