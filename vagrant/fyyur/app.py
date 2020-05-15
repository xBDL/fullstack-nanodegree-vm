#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from datetime import datetime
from sqlalchemy.sql import func


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120)) 
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
  start_time = db.Column(db.String(30))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  areas = {}

  venues = db.session.query(\
                Venue.id,\
                Venue.name,\
                Venue.city,\
                Venue.state,\
                func.count(Show.venue_id).label('num_shows'))\
                .join(Show, isouter=True)\
                .group_by(Venue)\
                .all()

  for venue in venues:

    city = venue.city.title()
    state = venue.state.upper()

    area = (city, state)
    if area not in areas:
      areas[area] = {'city': city, 
                     'state': state, 
                     'venues': []}

    print(f'----- {venue.name} has {venue.num_shows} shows -----', flush=True) ############################################################################delete

    areas[area]['venues'].append({'id': venue.id,
                                  'name': venue.name, 
                                  'num_upcoming_shows': venue.num_shows})

  areas = list(areas.values())

  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)
  venue.past_shows = []
  venue.upcoming_shows = []

  shows = Show.query.filter(venue.id==Show.venue_id) 
  for show in shows:
    artist = Artist.query.filter(show.artist_id==Artist.id).one()
    
    data = {'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time}

    if show.start_time < str(datetime.now()):
      venue.past_shows.append(data)
    
    else:
      venue.upcoming_shows.append(data)

  data = {'id': venue.id,
          'name': venue.name,
          'genres': venue.genres,
          'address': venue.address,
          'city': venue.city,
          'state': venue.state,
          'phone': venue.phone,
          'website': venue.website,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'image_link': venue.image_link,
          'past_shows': venue.past_shows,
          'upcoming_shows': venue.upcoming_shows,
          'past_shows_count': len(venue.past_shows),
          'upcoming_shows_count': len(venue.upcoming_shows)}

  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    new_venue = Venue(name = request.form['name'], 
                      genres = request.form.getlist('genres'), 
                      address = request.form['address'], 
                      city = request.form['city'], 
                      state = request.form['state'], 
                      phone = request.form['phone'], 
                      #website = 
                      facebook_link = request.form['facebook_link'], 
                      #seeking_talent = 
                      #seeking_description = 
                      #image_link = 
                      )

    try:
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    
    finally:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.with_entities(Artist.id, Artist.name)
  artists = [{'id': a.id, 'name': a.name} for a in artists]
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  artist.past_shows = []
  artist.upcoming_shows = []

  shows = Show.query.filter(artist.id==Show.artist_id) 
  for show in shows:
    venue = Venue.query.filter(show.venue_id==Venue.id).one()
    
    data = {'venue_id': show.venue_id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time}

    if show.start_time < str(datetime.now()):
      artist.past_shows.append(data)
    
    else:
      artist.upcoming_shows.append(data)

  artist = {'id': artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website, 
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link,
            'past_shows': artist.past_shows,
            'upcoming_shows': artist.upcoming_shows,
            'past_shows_count': len(artist.past_shows),
            'upcoming_shows_count': len(artist.upcoming_shows)}  

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    data = {'id': artist.id,
            'name': artist.name,
            'genres': artist.genres,
            'city': artist.city,
            'state': artist.state,
            'phone': artist.phone,
            'website': artist.website,
            'facebook_link': artist.facebook_link,
            'seeking_venue': artist.seeking_venue,
            'seeking_description': artist.seeking_description,
            'image_link': artist.image_link}    
    return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  artist = Artist.query.get(artist_id)

  for key in dir(artist):
    if key in request.form:
      setattr(artist, key, request.form[key])

  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  data = {'id': venue.id,
          'name': venue.name,
          'genres': venue.genres,
          'address': venue.address,
          'city': venue.city,
          'state': venue.state,
          'phone': venue.phone,
          'website': venue.website,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'image_link': venue.image_link}
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form

    new_artist = Artist(name = request.form['name'], 
                        genres = request.form['genres'], #DEBUG TODO
                        city = request.form['city'], 
                        state = request.form['state'], 
                        phone = request.form['phone'], 
                        #website = 
                        facebook_link = request.form['facebook_link'], 
                        #seeking_venue = 
                        #seeking_description = 
                        #image_link = 
                        )

    try:
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  
    finally:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = [] 

  shows = db.session.query(\
              Show,\
              Venue.name.label('venue_name'),\
              Artist.name.label('artist_name'),\
              Artist.image_link.label('artist_image_link'))\
            .select_from(Show)\
            .join(Venue, Show.venue_id==Venue.id)\
            .join(Artist, Show.artist_id==Artist.id)

  for show, venue_name, artist_name, artist_image_link in shows:
    data.append({'venue_id': show.venue_id,
                 'venue_name': venue_name,
                 'artist_id': show.artist_id,
                 'artist_name': artist_name,
                 'artist_image_link': artist_image_link,
                 'start_time': show.start_time})

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

    form = ShowForm(request.form)
    new_show = Show(venue_id = request.form['venue_id'],
                    artist_id = request.form['artist_id'],
                    start_time = request.form['start_time'])
  
    try:
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')  

    except:
        flash('An error occurred. Show could not be listed.')

    finally:
        return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
