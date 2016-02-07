from pyramid.config import Configurator


def main():
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator()
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('icon', '/favicon.ico')

    config.add_route('movie_list', '/show_movie')
    config.add_route('movie_json', '/movies')
    config.add_route('movies_seen_by_all', '/movies/seen_by_all')
    config.add_route('get_movie_by_id', '/movie/get/{movie_id}', request_method='GET')
    config.add_route('movie_details', '/movie/{movie_id}')

    config.add_route('user_list', '/users')
    config.add_route('add_user', '/users/add', request_method='POST')
    config.add_route('select_user', '/user/select/{user_id}')

    config.add_route('mark_watched', '/watched/{user_id}/{movie_id}/{rating}')

    config.add_route('scan', '/scan')

    config.add_route('delete_options', '/delete')
    config.add_route('delete_watched_by_all', '/delete/watched_by_all')

    config.add_route('repo_page', '/repo/page')
    config.add_route('list_repo', '/repo/list', request_method='POST')
    config.add_route('get_from_repo', '/repo/get', request_method='POST')

    config.scan()
    return config.make_wsgi_app()
