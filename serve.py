from movie_tracker.html_ui import main
from wsgiref.simple_server import make_server

app = main()
server = make_server("0.0.0.0", 8080, app)
server.serve_forever()
