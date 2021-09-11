# Task

Create a simple RESTful application with Django, Django Rest Framework, and other libraries you think are necessary for the implementation.

From user's perspective the app should have the following functionality:
- User can create movie entries.
- It should be allowed to create movie entry first and upload source media file later.
- Uploaded file is considered as valid media file if it has exact 1 video stream and 1 or more audio streams.
- Every uploaded media file should be re-encoded with specific parameters which are defined in settings and applied to all uploaded files.
- It should be possible to fetch the movie info as well as download the processed file.
- When fetching movie info, it should be possible to apply filters based on movie entry properties (e.g. name, description, status).

Choose the endpoint names which you believe are suitable for their functionality.
It's OK if you use sqlite3 as your DB backend instead of client-server RDBMS system like PostgreSQL or MySQL.
The application should be bundled into Docker image with instructions on how to run it and examples how to use it.
The source code should be uploaded to GitLab or GitHub.
If your application requires additional services (e.g. database server, storage server, application workers), please provide Docker-compose file to run the app and dependencies all together.
If you feel yourself comfortable with Gitlab CI and app deployment to cloud providers, you can optionally create GitLab pipeline configuration for building Docker image, pushing it to registry and deploying the app using cloud-provider of your choice (e.g. Google Cloud Platform, Amazon AWS, Heroku)


# TODO:
 * Deploy to clouds
 * Add tests
 * Add init db
 * Add download extend
 * Add Readme description
 * Add swagger
 * Add error handler
 * Add comments
 * Add Responses as classes
 * Add filename from film
 * Add typing

