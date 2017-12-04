import sys
import config
sys.path.append("..")
import eversign
from pprint import pprint
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

client = eversign.Client(config.access_key, config.business_id)


class myHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != '/':
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('not found'.encode())
            return

        document = eversign.Document()
        document.title = 'Title goes here'
        document.message = 'my message'

        # Enable embedded signing
        document.embedded_signing_enabled = True

        file = eversign.File(name='Test')
        file.file_url = 'raw.pdf'
        document.add_file(file)

        signer = eversign.Signer(name='Jane Doe', email=config.signer_email)
        signer.deliver_email = True # false is the default. set this to true to send an additional email to the signer
        document.add_signer(signer)

        field = eversign.SignatureField()

        field.identifier = 'Test'
        field.x = '120.43811219947'
        field.y = '479.02760463045'
        field.page = 1
        field.signer = 1
        field.width = 120
        field.height = 35
        field.required = 1
        document.add_field(field)

        finished_document = client.create_document(document)
        signing_url = finished_document.signers[0].embedded_signing_url
        print(signing_url)

        with open(dir_path + '/iframe.html', 'r') as myfile:
            template_html = myfile.read()

        template_html = '<script>var signingUrl = "' + \
            signing_url + '";</script>' + template_html

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send the html message
        self.wfile.write(template_html.encode())
        return

try:
    server = HTTPServer(('', 8000), myHandler)
    print('Started httpserver on http://localhost:8000')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
