__author__ = 'shanmuga'

import os
from configparser import ConfigParser

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

# Why this
Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"
    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    movie_name = Column(String)
    movie_file = Column(String)
    movie_file_size_mb = Column(Integer)
    subtitle_file = Column(String)
    status = Column(String)

    def make_dict(self):
        return {
            "movie_id": self.movie_id,
            "movie_name": self.movie_name,
            "movie_file": self.movie_file,
            "movie_file_size_mb": self.movie_file_size_mb,
            "subtitle_file": self.subtitle_file,
            "status": self.status
        }


class MovieWatchers(Base):
    __tablename__ = "movie_watchers"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)


class MovieViewings(Base):
    __tablename__ = "movie_viewings"
    movie_viewing_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("movie_watchers.user_id"))  # TODO set ondelete
    movie_id = Column(Integer, ForeignKey("movies.movie_id"))  # TODO set ondelete
    rating = Column(Integer)
    watched_at = Column(DateTime)  # TODO set default at now
    user = relationship("MovieWatchers", backref="movies_watched")
    movie = relationship("Movie", backref="watched_by")


class ConnectionManager:
    db_file_path = None
    engine = None
    session = None

    @classmethod
    def inittialize(cls, db_file_path):
        db_file_path = 'sqlite:///' + db_file_path
        cls.engine = create_engine(db_file_path, echo=False)
        cls.session = scoped_session(sessionmaker(bind=cls.engine))
        Base.metadata.create_all(cls.engine)


class ConfigManager:
    @classmethod
    def initialize(cls):
        cls.parser = ConfigParser()
        cls.parser.read("movie_tracker.ini")
        cls.db_file_path = cls.parser.get("system", "db_file")
        cls.extensions = cls.parser.get("system", "video_extensions").split(',')
        cls.monitor_dir = os.path.expandvars(cls.parser.get("system", "monitor_dir"))
        # validate
        if not os.path.isdir(cls.monitor_dir):
            raise ValueError("%s not a directory" % (cls.monitor_dir,))
        cls.extensions = ['.' + x.lower() for x in cls.extensions]


# Initalize config and ConnectionManager
ConfigManager.initialize()
ConnectionManager.inittialize(ConfigManager.db_file_path)


class DirMonitor:
    @classmethod
    def scan_directory(cls, monitor_dir, extensions):
        files_present = set()
        video_files = None
        for top, dirs, files in os.walk(monitor_dir):
            relative_top = top.replace(monitor_dir, '', 1)
            relative_top = relative_top[1:] if relative_top.startswith('/') else relative_top
            files_present = files_present.union(set(map(lambda x: os.path.join(relative_top, x), files)))
            video_files = list(filter(lambda x: os.path.splitext(x)[1].lower() in extensions, files_present))
        return video_files

    @classmethod
    def segregate(cls, video_files_found):
        session = ConnectionManager.session
        existing_movie_files = {x[0] for x in session.query(Movie.movie_file).all()}
        new_movie_files = set()
        present_movie_files = set()
        for video_file in video_files_found:
            if video_file in existing_movie_files:
                present_movie_files.add(video_file)
            else:
                new_movie_files.add(video_file)
        missing_movie_files = existing_movie_files.difference(present_movie_files)
        return new_movie_files, present_movie_files, missing_movie_files

    @classmethod
    def make_movie(cls, video_file):
        file_path = os.path.join(ConfigManager.monitor_dir, video_file)
        file_name = os.path.split(file_path)[1]
        movie_name = os.path.splitext(file_name)[0]
        movie_file_size_mb = os.path.getsize(file_path) / (1024.0 ** 2)
        return Movie(movie_name=movie_name, movie_file=video_file, movie_file_size_mb=movie_file_size_mb)

    @classmethod
    def populate(cls):
        session = ConnectionManager.session
        video_files_found = cls.scan_directory(ConfigManager.monitor_dir, ConfigManager.extensions)
        new_movie_files, present_movie_files, missing_movie_files = cls.segregate(video_files_found)
        missing_movies = session.query(Movie).filter(Movie.movie_file.in_(missing_movie_files)).all()
        new_movies = map(cls.make_movie, new_movie_files)
        for movie in missing_movies:
            session.delete(movie)
        for movie in new_movies:
            session.add(movie)
        session.commit()
        return len(new_movie_files), len(missing_movie_files)

    @classmethod
    def delete_movie_file(cls, movie):
        file_path = os.path.join(ConfigManager.monitor_dir, movie.movie_file)
        os.remove(file_path)


# def create_dummy_users():
#     user_lst = []
#     for i in range(10):
#         user_lst.append(MovieWatchers(user_name='user'+str(i)))
#     return user_lst

def create_dummy_movie_viewings(movies, users):
    from datetime import datetime

    movie_viewing_lst = []
    for movie, user in zip(movies, users):
        movie_viewing_lst.append(
                MovieViewings(movie_id=movie.movie_id, user_id=user.user_id, rating=1, watched_at=datetime.now()))
    return movie_viewing_lst


if __name__ == "__main__":
    session = ConnectionManager.session

    # Add all existing movies
    DirMonitor.populate()

    # for user in create_dummy_users():
    #     session.add(user)
    # session.commit()
    watchers = session.query(MovieWatchers).limit(4)
    movies = session.query(Movie).limit(4)
    movie_viewings = create_dummy_movie_viewings(movies, watchers)
    for movie_viewing in movie_viewings:
        session.add(movie_viewing)
    session.commit()

    viewings = session.query(MovieViewings).all()
    for movie_viewing in viewings:
        print(movie_viewing.user.user_name, movie_viewing.movie.movie_name, movie_viewing.movie.movie_file_size_mb,
              movie_viewing.watched_at, sep='\t')

    movies = session.query(Movie.movie_name, (Movie.movie_file_size_mb + 34).label("ab")).filter(
            Movie.movie_name.like('%0'))
    for movie in movies:
        print(movie.movie_name, movie.ab, sep='\t')
