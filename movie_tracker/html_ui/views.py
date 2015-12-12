from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render
from ..model.model import ConnectionManager, Movie, MovieWatchers

from time import sleep

session = ConnectionManager.session

# @view_config(route_name='home', renderer='templates/movies.jinja2')
@view_config(route_name='movie_list')
def list_movies(request):
    current_user = None
    if (request.cookies.get('user_id')):
        current_user_id = request.cookies['user_id']
        current_user = session.query(MovieWatchers).filter(MovieWatchers.user_id == current_user_id).one()
    movies = session.query(Movie).limit(100).all()
    print(len(movies))
    total_movies = session.query(Movie).count()
    template_html = render('templates/movies.jinja2',
                      {'project_name':'movie_tracker', 'movie_count': total_movies, 'moveis':movies, 'current_user':current_user})
    return Response(template_html)

@view_config(route_name="movie_details")#, renderer="templates/movie_details.jinja2")
def movie_detail(request):
    movie = session.query(Movie).filter(Movie.movie_id == request.matchdict['movie_id']).one()
    render_dict = dict(request.matchdict, **{'project_name':'Movie Tracker', 'movie':movie})
    template_html = render("templates/movie_details.jinja2", render_dict)
    return Response(template_html)

@view_config(route_name="user_list")
def listUsers(request):
    users = session.query(MovieWatchers).all()
    template_html = render('templates/users.jinja2', {'users':users, 'project_name':'Movie Tracker'})
    return Response(template_html)

@view_config(route_name="select_user")
def select_user(request):
    user_id = request.matchdict['user_id']
    response = Response(status=302, location="/home")
    response.set_cookie('user_id', user_id)
    return response

@view_config(route_name='icon')
def icon(request):
    import os
    file_path  = os.path.dirname(__file__) + '/static/favicon.ico'
    with open(file_path, 'rb') as fin:
        response = Response(fin.read())
        response.content_type  = 'image/x-icon'
    return response
