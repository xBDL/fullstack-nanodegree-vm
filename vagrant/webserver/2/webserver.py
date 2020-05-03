from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

from db_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += f"{restaurant.name}<br />"
                    output += "<a href='#'>Edit</a><br />"
                    output += "<a href='#'>Delete</a><br /><br />"
                output += "</body></html>"
                
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

def main():
    try:
        print('Web server running...open localhost:8080/restaurants in your browser')
        server = HTTPServer(('', 8080), webServerHandler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
