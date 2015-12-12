from pyramid.config import Configurator


def main():
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator()
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('movie_details', '/movie/{movie_id}')
    config.add_route('icon', '/favicon.ico')
    config.scan()
    return config.make_wsgi_app()
