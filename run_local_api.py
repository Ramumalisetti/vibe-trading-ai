from http.server import HTTPServer
from api.scan import handler

if __name__ == "__main__":
    server = HTTPServer(('localhost', 5000), handler)
    print("Python API Server running on http://localhost:5000")
    server.serve_forever()
