"""
http
~~~~

A web interface for mod:`charex`.
"""
from unicodedata import normalize

from flask import Flask, make_response, request, send_from_directory

from charex import charex


# Create the web application.
app = Flask(__name__)


# Utility functions.
def search_data(query: str) -> tuple[str, ...]:
    raise RuntimeError('Calamity!')


def shutdown_server():
    """Shutdown the server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def sanitize(value: str) -> str:
    """Sanitize input."""
    bad = ["'", '"', '<']
    for char in bad:
        if char in value:
            raise ValueError('Disallowed character used.')
    return value


# Responders.
@app.route('/badresult', methods=['GET',])
def badresult():
    """The vulnerable result response."""
    # Validate input.
    untrust = request.args['q']
    clean = sanitize(untrust)            # Sanitization avoids bad characters.

    # Perform the search.
    normal = normalize('NFKC', clean)    # Normalization can undo sanitization.
    try:
        result = search_data(normal)
        # Cutting lines to format results for display.
        return result

    # Display error if search errors.
    except RuntimeError:
        lines = charex.read_resource('result')
        doc = ''.join(lines)
        resp = make_response(doc.format(normal))    # Unsanitary input.
        return resp


@app.route('/goodresult', methods=['GET',])
def goodresult():
    """The less vulnerable result response."""
    # Validate input.
    untrust = request.args['q']
    normal = normalize('NFKC', untrust)  # Normalization first.
    clean = sanitize(normal)             # Sanitization avoids bad characters.

    # Perform the search.
    try:
        result = search_data(clean)
        # Cutting lines to format results for display.
        return result

    # Display error if search errors.
    except RuntimeError:
        lines = charex.read_resource('result')
        doc = ''.join(lines)
        resp = make_response(doc.format(clean))     # Sanitary input.
        return resp


@app.route('/quote', methods=['GET',])
def quote():
    """Demonstrate character set differences."""
    codec = 'cp1252'
    if 'charset' in request.args:
        codec = request.args['charset']
    lines = charex.read_resource('quote', codec=codec)
    doc = ''.join(line for line in lines)
    resp = make_response(doc)
    return resp


@app.route('/shutdown', methods=['GET',])
def shutdown():
    """Process request to shutdown the server."""
    shutdown_server()
    return 'Shutting down'


@app.route('/styles/<path:path>')
def styles(path):
    """Serve static files."""
    return send_from_directory('static/styles', path)


# Mainline.
if __name__ == '__main__':
    app.run(port=8080, debug=True)
