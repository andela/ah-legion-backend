[![Build Status](https://travis-ci.com/andela/ah-legion-backend.svg?branch=develop)](https://travis-ci.com/andela/ah-legion-backend)
[![Coverage Status](https://coveralls.io/repos/github/andela/ah-legion-backend/badge.svg?branch=develop)](https://coveralls.io/github/andela/ah-legion-backend?branch=develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/72c25fc53cfdf26f49d7/maintainability)](https://codeclimate.com/github/andela/ah-legion-backend/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/72c25fc53cfdf26f49d7/test_coverage)](https://codeclimate.com/github/andela/ah-legion-backend/test_coverage)

Authors Haven - A Social platform for the creative at heart.
=======

## Vision
Create a community of like minded authors to foster inspiration and innovation
by leveraging the modern web.

## Running the app.
Authors Haven app can be run by:
### STEP 1:
    Git clone this repository: `git clone https://github.com/andela/ah-legion-backend.git`

### STEP 2: 
    Change your working directory to the app's root. `cd ah-legion-backend`

### STEP 3:
    Create a virtual environment and activate it.
    Install all the requirements by running `pip install -r requirements.txt`
    Create an environment file with environment variables in the following format:
  
      SECRET_KEY=supersecretkey
      DEBUG=True
      DB_NAME=yourdbname
      DB_USER=yourname
      DB_PASSWORD=yourstrongpassword
      DB_HOST=127.0.0.1

### STEP 4:
    Run the app according to the environment you need:

   #### Development environment:
    `python manage.py makemigrations --settings=authors.settings.dev`

    `python manage.py migrate --settings=authors.settings.dev`

    `python manage.py runserver --settings=authors.settings.dev`

   #### Testing environment:
    `python manage.py test --settings=authors.settings.test`

   #### Production environment:
     The run the app on a production environment:
     Use Postman to acccess the app by using this url as your domain:
     `https://ah-legion.herokuapp.com`

     Input appropriate endpoint urls, enjoy.

## API Spec
The preferred JSON object to be returned by the API should be structured as follows:

### Users (for authentication)

```source-json
{
  "user": {
    "email": "jake@jake.jake",
    "token": "jwt.token.here",
    "username": "jake",
    "bio": "I work at statefarm",
    "image": null
  }
}
```
### Profile
```source-json
{
  "profile": {
    "username": "jake",
    "bio": "I work at statefarm",
    "image": "image-link",
    "following": false
  }
}
```
### Single Article
```source-json
{
  "article": {
    "slug": "how-to-train-your-dragon",
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "It takes a Jacobian",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }
}
```
### Multiple Articles
```source-json
{
  "articles":[{
    "slug": "how-to-train-your-dragon",
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "It takes a Jacobian",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }, {

    "slug": "how-to-train-your-dragon-2",
    "title": "How to train your dragon 2",
    "description": "So toothless",
    "body": "It a dragon",
    "tagList": ["dragons", "training"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }],
  "articlesCount": 2
}
```
### Single Comment
```source-json
{
  "comment": {
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }
}
```
### Multiple Comments
```source-json
{
  "comments": [{
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "jake",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }],
  "commentsCount": 1
}
```
### List of Tags
```source-json
{
  "tags": [
    "reactjs",
    "angularjs"
  ]
}
```
### Errors and Status Codes
If a request fails any validations, expect errors in the following format:

```source-json
{
  "errors":{
    "body": [
      "can't be empty"
    ]
  }
}
```
### Other status codes:
401 for Unauthorized requests, when a request requires authentication but it isn't provided

403 for Forbidden requests, when a request may be valid but the user doesn't have permissions to perform the action

404 for Not found requests, when a resource can't be found to fulfill the request


Endpoints:
----------

### Authentication:

`POST /api/users/login`

Example request body:

```source-json
{
  "user":{
    "email": "jake@jake.jake",
    "password": "jakejake"
  }
}
```

No authentication required, returns a User

Required fields: `email`, `password`

### Registration:

`POST /api/users`

Example request body:

```source-json
{
  "user":{
    "username": "Jacob",
    "email": "jake@jake.jake",
    "password": "jakejake"
  }
}
```

No authentication required, returns a User

Required fields: `email`, `username`, `password`

### Get Current User

`GET /api/user`

Authentication required, returns a User that's the current user

### Update User

`PUT /api/user`

Example request body:

```source-json
{
  "user":{
    "email": "jake@jake.jake",
    "bio": "I like to skateboard",
    "image": "https://i.stack.imgur.com/xHWG8.jpg"
  }
}
```

Authentication required, returns the User

Accepted fields: `email`, `username`, `password`, `image`, `bio`

### Reset Password

`POST /api/users/password-reset/`

Example request body:

```source-json
{
            "payload": {
                "email": "jake@jake.com",
                "callback_url": "https://legion.com"

            }
        }
```

Requires a registered user, returns a message, sends an email to given address

Accepted fields: `email`, `callback_url`


`PUT /api/users/password-reset/`

Example request body:

```source-json
{
  "user_password":{
    "password": "jake123son",
    "confirm_password": "jake123son",
    "token":"valid-token"
  }
}
```

Requires a registered user and a token contained in the link sent to the supplied email address, returns a message

Accepted fields: `password`, `new_password`, `token`


### Get Profile

`GET /api/profiles/:username`

Authentication optional, returns a Profile

### Follow user

`POST /api/profiles/:username/follow`

Authentication required, returns a Profile

No additional parameters required

### Unfollow user

`DELETE /api/profiles/:username/follow`

Authentication required, returns a Profile

No additional parameters required

### List Articles

`GET /api/articles`

Returns most recent articles globally by default, provide `tag`, `author` or `favorited` query parameter to filter results

Query Parameters:

Filter by tag:

`?tag=AngularJS`

Filter by author:

`?author=jake`

Favorited by user:

`?favorited=jake`

Limit number of articles (default is 20):

`?limit=20`

Offset/skip number of articles (default is 0):

`?offset=0`

Authentication optional, will return multiple articles, ordered by most recent first

### Feed Articles

`GET /api/articles/feed`

Can also take `limit` and `offset` query parameters like List Articles

Authentication required, will return multiple articles created by followed users, ordered by most recent first.

### Get Article

`GET /api/articles/:slug`

No authentication required, will return single article

### Create Article

`POST /api/articles/create`

Example request body:

```source-json
{
  "article": {
    "title": "How to train your dragon",
    "description": "Ever wonder how?",
    "body": "You have to believe",
    "tagList": ["reactjs", "angularjs", "dragons"]
  }
}
```

Authentication required, will return an Article

Required fields: `title`, `description`, `body`

Optional fields: `tagList` as an array of Strings

### Update Article

`PUT /api/articles/:slug/edit`

Example request body:

```source-json
{
  "article": {
    "title": "Did you train your dragon?"
  }
}
```

Authentication required, returns the updated Article

Optional fields: `title`, `description`, `body`

The `slug` does not get updated when the `title` is changed

### Delete Article

`DELETE /api/articles/:slug/edit`

Authentication required

### Pubish Article

`PATCH /api/articles/:slug/publish`

Authentication required

### Add Comments to an Article

`POST /api/articles/:slug/comments`

Example request body:

```source-json
{
  "comment": {
    "body": "His name was my name too."
  }
}
```

Authentication required, returns the created Comment
Required field: `body`

### Get Comments from an Article

`GET /api/articles/:slug/comments`

Authentication optional, returns multiple comments

### Delete Comment

`DELETE /api/articles/:slug/comments/:id`

Authentication required

### Favorite Article

`POST /api/articles/:slug/favorite`

Authentication required, returns the Article
No additional parameters required

### Unfavorite Article

`DELETE /api/articles/:slug/favorite`

Authentication required, returns the Article

No additional parameters required

### Get Tags

`GET /api/tags`

## Create an Article Rating

`POST /api/articles/<slug>/rate/`

Example request body:

```source-json
{
	"rating":{
		"value":"3",
		"review":"Quite interesting."
	}
}
```

Requires authentication

Accepted fields: `value`, `review`

## Update an Article Rating

`PUT api/articles/<slug>/rate/`

Example request body:

```source-json
{
	"rating":{
		"value":"4",
		"review":"Quite interesting. I loved the ending."
	}
}
```

Requires authentication

Accepted fields: `value`, `review`

## Get an Article's Ratings

`GET api/articles/<slug>/ratings/`


Returns all reviews attached to an article



