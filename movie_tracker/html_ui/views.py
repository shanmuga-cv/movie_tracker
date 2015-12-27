import json
import os
from datetime import datetime

from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config

from ..model.model import ConnectionManager, Movie, MovieWatchers, MovieViewings, DirMonitor

session = ConnectionManager.session
global_render_dict = {'project_name': 'Movie Tracker'}


def get_render_dict(request):
    current_user = None
    if (request.cookies.get('user_id')):
        current_user_id = request.cookies['user_id']
        current_user = session.query(MovieWatchers).filter(MovieWatchers.user_id == current_user_id).one_or_none()
    render_dict = dict(global_render_dict, current_user=current_user)
    return render_dict


# @view_config(route_name='home', renderer='templates/movies.jinja2')
@view_config(route_name='movie_list')
def movie_list_page(request):
    render_dict = get_render_dict(request)
    template_html = render('templates/movie_list.jinja2', render_dict)
    return Response(template_html)


@view_config(route_name='movie_json')
def movies_json(request):
    movies = session.query(Movie).all()
    json_list = json.dumps([movie.make_dict() for movie in movies])
    return Response(body=json_list, content_type="text/json")


@view_config(route_name="movie_details")  # renderer="templates/movie_details.jinja2")
def movie_detail(request):
    render_dict = get_render_dict(request)
    movie = session.query(Movie).filter(Movie.movie_id == request.matchdict['movie_id']).one()
    current_user = render_dict.get('current_user')
    if current_user:
        previous_viewing = session.query(MovieViewings).filter((MovieViewings.movie_id == movie.movie_id) & \
                                                               (MovieViewings.user_id == current_user.user_id)) \
            .one_or_none()
        previous_rating = previous_viewing.rating if previous_viewing else ""
        render_dict['previous_rating'] = previous_rating
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
    response = Response(status=302, location="/")
    response.set_cookie('user_id', user_id)
    return response


@view_config(route_name='icon')
def icon(request):
    file_path = os.path.dirname(__file__) + '/static/favicon.ico'
    with open(file_path, 'rb') as fin:
        response = Response(fin.read())
        response.content_type = 'image/x-icon'
    return response


@view_config(route_name='mark_watched')
def mark_watched(request):
    movie_id = request.matchdict['movie_id']
    user_id = request.matchdict['user_id']
    rating = float(request.matchdict['rating'])
    previous_Viewing = session.query(MovieViewings).filter((MovieViewings.movie_id == movie_id) & \
                                                           (MovieViewings.user_id == user_id)).one_or_none()
    if (previous_Viewing):
        previous_Viewing.rating = rating
        session.merge(previous_Viewing)
    else:
        viewing = MovieViewings(movie_id=movie_id, user_id=user_id, rating=rating, watched_at=datetime.now())
        session.add(viewing)
    session.commit()
    response = Response(status=302, location="/movies")
    return response


@view_config(route_name="home")
def home(request):
    render_dict = get_render_dict(request)
    template_html = render('templates/home.jinja2', render_dict)
    return Response(template_html)


@view_config(route_name="add_user")
def add_user(request):
    user_name = request.POST['user_name']
    user = MovieWatchers(user_name=user_name)
    session.add(user)
    session.commit()
    return Response(status=302, location="/users")


@view_config(route_name="scan")
def scan(request):
    total_new_movies_found, total_movies_deleted = DirMonitor.populate()
    body = '{"total_new_movies_found": %d, "total_movies_deleted": %d}' % (total_new_movies_found, total_movies_deleted)
    return Response(body=body, content_type="text/json")


@view_config(route_name='delete_options')
def delete(request):
    render_dict = get_render_dict(request)
    return Response(render('/templates/delete.jinja2', render_dict))


@view_config(route_name='delete_watched_by_all')
def delete_watched_by_all(request):
    total_users = session.query(MovieWatchers).count()
    cur = session.execute(
            "select movie_id from (select movie_id, count(distinct(user_id)) cnt_users from movie_viewings group by movie_id ) where cnt_users =%d" % (
            total_users,))
    movie_ids = map(lambda x: x.movie_id, cur)
    movies = session.query(Movie).filter(Movie.movie_id.in_(movie_ids)).all()
    for movie in movies:
        DirMonitor.delete_movie_file(movie)
        session.delete(movie)
    session.commit()
    message = '{"movies_deleted": %d}' % (len(movies),)
    return Response(body=message, content_type='text/json')
