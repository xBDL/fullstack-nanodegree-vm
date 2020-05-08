


# NOTES
- Use `source env/scripts/activate` instead of `source env/bin/activate`

- PostgreSQL superuser password is `password`




# TODO
Connect to a database in config.py. A project submission that uses a local database connection is fine.

Using SQLAlchemy, set up normalized models for the objects we support in our web app in the Models section of app.py. Check out the sample pages provided at /artists/1, /venues/1, and /shows/1 for examples of the data we want to model, using all of the learned best practices in database schema design. Implement missing model properties and relationships using database migrations via Flask-Migrate.

Implement form submissions for creating new Venues, Artists, and Shows. There should be proper constraints, powering the /create endpoints that serve the create form templates, to avoid duplicate or nonsensical form submissions. Submitting a form should create proper new records in the database.

Implement the controllers for listing venues, artists, and shows. Note the structure of the mock data used. We want to keep the structure of the mock data.

Implement search, powering the /search endpoints that serve the application's search functionalities.

Serve venue and artist detail pages, powering the <venue|artist>/<id> endpoints that power the detail pages.
