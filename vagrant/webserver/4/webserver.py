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
            ### LIST ALL RESTAURANTS ------------------------------------------
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ("<html><body>"
                          "<h1><a href='/restaurants/new'>Make a New Restaurant Here</a></h1><br /><br />")
                restaurants = session.query(Restaurant).all()
                for restaurant in restaurants:
                    output += (f"{restaurant.name}<br />"
                               f"<a href='/restaurants/{restaurant.id}/edit'>Edit</a><br />"
                               "<a href='#'>Delete</a><br /><br />")
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            ### ADD A NEW RESTAURANT ------------------------------------------
            elif self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ("<html><body>"
                          "<h1>Make a New Restaurant</h1>"
                          "<form method='POST' enctype='multipart/form-data' accept-charset='utf-8' action='/restaurants/new'>"
                          "<input name='newRestaurantName' type='text' placeholder='New Restaurant Name'>"
                          "<input type='submit' value='Create'>"
                          "</form></body></html>")
                self.wfile.write(output.encode())
                return

            ### EDIT A RESTAURANT ---------------------------------------------
            elif self.path.endswith("/edit"):
                restaurant_id_path = self.path.split("/")[2]
                my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()
                if my_restaurant_query:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = (f"<html><body><h1>{my_restaurant_query.name}</h1>"
                              f"<form method='POST' enctype='multipart/form-data' accept-charset='utf-8' action='/restaurants/{restaurant_id_path}/edit'>"
                              f"<input name='newRestaurantName' type='text' placeholder='{my_restaurant_query.name}'>"
                              "<input type='submit' value='Rename'></form></body></html>")
                    self.wfile.write(output.encode())

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)



    def do_POST(self):
        try:
            ### ADD NEW RESTAURANT --------------------------------------------
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

            ### EDIT A RESTAURANT ---------------------------------------------
            if self.path.endswith("/edit"):
                # HEADERS are now in dict/json style container
                ctype,pdict = cgi.parse_header(self.headers['content-type'])
                if ctype == 'multipart/form-data':
                    # boundary data needs to be encoded in a binary format
                    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                    # Added 1 debug line here
                    pdict['CONTENT-LENGTH'] = int(self.headers['content-length'])
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurant_id_path = self.path.split("/")[2]
                    my_restaurant_query = session.query(Restaurant).filter_by(id=restaurant_id_path).one()
                    if my_restaurant_query != []:
                        my_restaurant_query.name = messagecontent[0]
                        session.add(my_restaurant_query)
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
