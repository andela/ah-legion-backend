user2 = {
    "user": {
        "username": "Josh",
        "email": "joshmoracha@gmail.com",
        "password": "password",
        'callback_url': 'http://www.youtube.com'
    }
}

user1 = {
    "user": {
        "username": "Moracha",
        "email": "jratcher@gmail.com",
        "password": "password",
        'callback_url': 'http://www.youtube.com'
    }
}
article = {
    "article": {
        "title": "How to train your dragon",
        "description": "Ever wonder how?",
        "body": "You have to believe",
        "tagList": ["reactjs", "angularjs", "dragons"]
    }
}

like_data = {
	"is_like": True
}

valid_rate_data1 = {"rating":
{"value": "2",
"review": "How do you train your dragon?"}}

valid_rate_data2 = {"rating":
{"value": "3","review": ""}
}

update_rating_data = {"rating": {
"value": "3",
"review": "That's great!"
}
}

valid_data_rasponse = {
    "message": "Article rated."
}

author_rating_data_response = {
    "message": "You cannot rate your own article."
}

no_ratings_data_response = "This article has not been rated."

non_existent_article_response = {
    "message": "This article was not found."
}
no_review_data_response = {
    "message": "This article has no reviews."
}

rating_twice_data_response = {
    "message": "You have already rated this article."
}

update_rating_data_response = {
    "message": "Rating updated."
}

not_rated_data_response ={
"message": "You have not rated this article."
}
