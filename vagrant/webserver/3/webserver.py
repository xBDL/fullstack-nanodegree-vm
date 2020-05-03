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

                output = ("<html><body>"
                          "<a href='/restaurants/new'>Make a New Restaurant Here</a><br />")
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += (f"{restaurant.name}<br />"
                               "<a href='#'>Edit</a><br />"
                               "<a href='#'>Delete</a><br /><br />")
                output += "</body></html>"
                
                self.wfile.write(output.encode())
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ("<html><body>"
                          "<h1>Make a New Restaurant</h1>"
                          "<form method='POST' enctype='multipart/form-data' "
                          "accept-charset='utf-8' action='/restaurants/new'>"
                          "<input name='newRestaurantName' type='text' placeholder='New Restaurant Name'>"
                          "<input type='submit' value='Create'>"
                          "</form></body></html>")
                
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)



    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                
                # HEADERS are now in dict/json style container
                ctype,pdict = cgi.parse_header(self.headers['content-type'])

                if ctype == 'multipart/form-data':

                    # boundary data needs to be encoded in a binary format
                    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                    # Added 1 debug line here
                    pdict['CONTENT-LENGTH'] = int(self.headers['content-length'])

                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name=messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except:
            raise

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
