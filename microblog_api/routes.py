from .resources import (SigninView, SignupView, UsersRatingView,
                        PostListCreateView, PostUpdateDeleteView)


def setup_routes(app):
    app.router.add_view('/v1/users/signup', SignupView, name='signup')
    app.router.add_view('/v1/users/signin', SigninView, name='signin')
    app.router.add_view('/v1/users/rating', UsersRatingView, name='rating')

    app.router.add_view('/v1/posts', PostListCreateView, name='list_create_post')
    app.router.add_view('/v1/posts/{nickname:\w+}', PostUpdateDeleteView, name='user_posts')
