import http.server
import socketserver

PORT = 8000

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Docker Test OK! Servidor corriendo en contenedor.</h1>")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), SimpleHandler) as httpd:
        print(f"🚀 Servidor escuchando en el puerto {PORT}...")
        httpd.serve_forever()
