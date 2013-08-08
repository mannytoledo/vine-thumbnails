from StringIO import StringIO

from flask import (
    Flask, make_response, request, render_template, redirect, url_for)
import requests
from bs4 import BeautifulSoup
from PIL import Image


app = Flask(__name__)


@app.route('/')
def index():
    """Renders a simple form for choosing a Vine and size."""
    vine_id = request.args.get('vine_id')
    size = request.args.get('s')

    if vine_id and size:
        return redirect(url_for('vine_thumb', vine_id=vine_id, s=size))

    return render_template('index.html')


@app.route('/t/<vine_id>/')
def vine_thumb(vine_id):
    """Get a Vine video thumbnail.

    Add ?s=SIZE to the URL to specify the maximum width of the thumbnail.
    Vine "poster" images are 480x480.
    """
    response = requests.get('http://vine.co/v/%s' % vine_id)

    if response.status_code != 200:
        return 'Whoops!', 404

    try:
        size = (int(request.args.get('s', 480)), 480)
    except ValueError:
        size = (480, 480)

    # Get the poster URL from the <video> tag
    parsed = BeautifulSoup(response.content)
    poster_url = parsed.video['poster']

    poster_content = StringIO(requests.get(poster_url).content)
    poster = Image.open(poster_content)

    # Resize the poster and save it in a new StringIO
    poster.thumbnail(size, Image.ANTIALIAS)
    saved_poster = StringIO()
    poster.save(saved_poster, 'JPEG')

    response = make_response(saved_poster.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'

    return response, 200


if __name__ == '__main__':
    app.run(debug=True)