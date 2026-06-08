from waitress import serve
from Signature.wsgi import application

serve(application, host='0.0.0.0', port=8060, threads=8)