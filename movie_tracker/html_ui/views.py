from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render
from ..model.model import ConnectionManager, Movie

from time import sleep

session = ConnectionManager.session

# @view_config(route_name='home', renderer='templates/home.pt')
@view_config(route_name='home')
def my_view(request):
    movies = session.query(Movie).limit(100).all()
    print(len(movies))
    total_movies = session.query(Movie).count()
    template = render('templates/home.jinja2',
                      {'project_name':'movie_tracker', 'movie_count': total_movies, 'moveis':movies})
    return Response(template)

@view_config(route_name="movie_details")#, renderer="templates/movie_details.jinja2")
def movie_detail(request):
    movie = session.query(Movie).filter(Movie.movie_id == request.matchdict['movie_id']).one()
    render_dict = dict(request.matchdict, **{'project_name':'I don\'t care', 'movie':movie})
    template_html = render("templates/movie_details.jinja2", render_dict)
    return Response(template_html)

@view_config(route_name='icon')
def icon(request):
    import os
    file_path  = os.path.dirname(__file__) + '/static/favicon.ico'
    with open(file_path, 'rb') as fin:
        response = Response(fin.read())
        response.content_type  = 'image/x-icon'
    return response
