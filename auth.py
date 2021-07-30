from .config import config

from flask import request, redirect
import requests
from requests.utils import quote
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user
import hmac


def get_state_secret(app, user):
    return hmac.new(
        app.config['DISCORD_AUTH_SECRET'].encode('utf8'),
        user.id.to_bytes(8, 'big'),
        'sha256'
    ).hexdigest()

def load(app):
    config(app)

    @app.route("/discordauth", methods=['GET'])
    @authed_only
    def discordauth():
        error = request.values.get('error')
        if error:
            return error

        user = get_current_user()

        code = request.args.get('code')
        if code is None:
            return redirect(
                "https://discord.com/oauth2/authorize?response_type=code" +
                "&client_id=" + quote(app.config['DISCORD_AUTH_CLIENT_ID']) +
                "&redirect_uri=" + quote(request.base_url) +
                "&scope=identify" +
                "&state=" + quote(get_state_secret(app, user))
                , code=302)

        if not hmac.compare_digest(get_state_secret(app, user), request.args.get('state')):
            return "No csrf pls"

        r = requests.post('https://discord.com/api/v8/oauth2/token', data={
            'client_id': app.config['DISCORD_AUTH_CLIENT_ID'],
            'client_secret': app.config['DISCORD_AUTH_SECRET'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': request.base_url
        }, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        # intentional throw (500) on bad code, todo make better error?
        r.raise_for_status()
        access_token = r.json()['access_token']
        access_details = r.text

        r = requests.get('https://discord.com/api/v8/users/@me', headers={
            'Authorization': 'Bearer ' + access_token
        })
        r.raise_for_status()

        info = ("User profile: " + request.url_root + "users/" + str(user.id) + "\n" +
            "User admin: " + request.url_root + "admin/users/" + str(user.id) + "\n" +
            "<@" + str(r.json()['id']) + ">\n" +
            "```\n" + access_details + "``` ```\n" + r.text + "```")

        requests.post(app.config['DISCORD_AUTH_WEBHOOK'], json={
            'content': info
        })

        return "Completed successfully"
