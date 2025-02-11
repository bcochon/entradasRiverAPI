from flask import Flask, request, Response, json
from scraper import get_noticias, get_partidos
app = Flask('entradasRiver')

@app.route('/')
def api_root():
    return ''

@app.route('/anuncios')
def api_announcements():
    if 'num' in request.args:
        noticias = get_noticias(int(request.args['num']))
    else:
        noticias = get_noticias()
    return json.dumps(noticias)

@app.route('/partidos')
def api_matches():
    if 'num' in request.args:
        partidos = get_partidos(int(request.args['num']))
    else:
        partidos = get_partidos()
    return json.dumps(partidos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)