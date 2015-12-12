from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render
from ..model.model import ConnectionManager, Movie, MovieWatchers

from time import sleep

session = ConnectionManager.session
global_render_dict = {'project_name': 'Movie Tracker'}
def get_render_dict(request):
    current_user = None
    if (request.cookies.get('user_id')):
        current_user_id = request.cookies['user_id']
        current_user = session.query(MovieWatchers).filter(MovieWatchers.user_id == current_user_id).one()
    render_dict = dict(global_render_dict, current_user=current_user)
    return render_dict

# @view_config(route_name='home', renderer='templates/movies.jinja2')
@view_config(route_name='movie_list')
def list_movies(request):
    render_dict = get_render_dict(request)
    movies = session.query(Movie).limit(100).all()
    print(len(movies))
    total_movies = session.query(Movie).count()
    render_dict['movie_count'] = total_movies
    render_dict['movies'] = movies
    template_html = render('templates/movies.jinja2', render_dict)
    return Response(template_html)

@view_config(route_name="movie_details")#, renderer="templates/movie_details.jinja2")
def movie_detail(request):
    render_dict = get_render_dict(request)
    movie = session.query(Movie).filter(Movie.movie_id == request.matchdict['movie_id']).one()
    render_dict['movie'] = movie
    template_html = render("templates/movie_details.jinja2", render_dict)
    return Response(template_html)

@view_config(route_name="user_list")
def listUsers(request):
    render_dict = get_render_dict(request)
    users = session.query(MovieWatchers).all()
    render_dict['users'] = users
    template_html = render('templates/users.jinja2', render_dict)
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
