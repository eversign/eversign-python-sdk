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

        document_template = eversign.Template()
        document_template.template_id = config.template_id
        document_template.title = 'Tile goes here'
        document_template.message = 'my message'

        # Enable embedded signing
        document_template.embedded_signing_enabled = True

        signer = eversign.Signer(
            name='Jane Doe', email=config.signer_email, role='Client')
        document_template.add_signer(signer)

        field = eversign.TextField()
        field.identifier = config.field_identifier
        field.value = 'value 1'
        document_template.add_field(field)

        finished_document = client.create_document_from_template(
            document_template)
        signing_url = finished_document.signers[0].embedded_signing_url
        pprint(signing_url)

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
