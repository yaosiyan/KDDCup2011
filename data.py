#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
Python source code - replace this with a description of the code and write the code below this text.
"""

__author__ = [ 'Patrick Butler', "Depbrakash Patnaik" ]
__email__  = [ 'pabutler@vt.edu', "patnaik@vt.edu" ]

import time
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relation, backref,create_session
from sqlalchemy.ext.declarative import declarative_base
import datetime

engine = create_engine('postgresql:///kddcuptest')
#engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(autocommit = False, autoflush = True)
Session.configure(bind=engine)
metadata = MetaData()
session = Session()

Base = declarative_base(engine, metadata)

class SQLData:
    @classmethod
    def select(cls):
        return session.query(cls)
    def add(self):
        return session.add(self)
    def save(self):
        return session.save(self)
    def delete(self):
        return session.delete(self)

album_genre = Table('association', Base.metadata,
    Column('album_id', Integer, ForeignKey('albums.album_id')),
    Column('genre_id', Integer, ForeignKey('genres.genre_id'))
)

class User(Base,SQLData):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)

    def __init__(self, user_id): #title=None, num_words=None, time=None, hash=None):
        self.user_id = user_id

    def __repr__(self):
        return "<User: %d>" % self.user_id

class Rating(Base, SQLData):
    __tablename__ = 'ratings'
    rating_id  = Column(Integer, primary_key=True, autoincrement=True)
    item_id  = Column(Integer) #, primary_key=True)
    timestamp          = Column(DateTime)
    score = Column(Integer)
    user_id   = Column(Integer, ForeignKey('users.user_id'))
    user = relation(User, backref=backref('ratings'))

    def __init__(self, item_id = None, timestamp = None, score= None, user=None):
        self.rating_id = None #rating_id
        self.item_id = item_id
        self.timestamp = timestamp
        self.score = score
        self.user = user

    def __repr__(self):
        return "<Rating(%s): %s of %s @ %s>" % (self.rating_id, self.item_id,
                self.score, self.timestamp)


class Genre(Base, SQLData):
    __tablename__ = 'genres'
    genre_id = Column(Integer, primary_key=True)
    def __init__(self, genre_id = None):
        self.genre_id = genre_id

class Artist(Base, SQLData):
    __tablename__ = 'artists'
    artist_id = Column(Integer, primary_key=True)

    def __init__(self, artist_id = None):
       self.artist_id = artist_id

class Album(Base, SQLData):
    __tablename__ = 'albums'
    album_id = Column(Integer, primary_key=True)
    artist_id   = Column(Integer, ForeignKey('artists.artist_id'))
    artist = relation(Artist, backref=backref('albums'))
    genres = relation("Genre", secondary=album_genre, backref="albums")

    def __init__(self, album_id = None, artist = None):
        self.album_id = album_id
        if isinstance(artist, int):
            self.artist_id = artist
        else:
            self.artist = artist

    def __repr__(self):
        return "<Album(%s): by %s in %d genres>" % ( self.album_id,
                self.artist_id, len(self.genres))

def readDatas(dir):
    start = time.time()

    artistdata = open(os.path.join(dir, "artistData1.txt" ))
    for line in artistdata:
        id = int( line.strip())
        artist = Artist(id)
        artist.add()
    artistdata.close()

    print "."

    genredata = open(os.path.join(dir, "genreData1.txt" ))
    for line in  genredata:
        id = int( line.strip())
        genre = Genre(id)
        genre.add()
    genredata.close()
    session.commit()

    print "."
    albumdata = open(os.path.join(dir, "albumData1.txt" ))
    for line in albumdata:
        row = line.strip().split("|")
        id = int(row[0])
        if row[1] == "None":
            artistid = None
        else:
            artistid = int(row[1])
        album = Album(id, artistid)
        session.flush()
        if len(row) >= 3 and row[2] != "None":
            genres = map(int, row[2:])
            album.genres = Genre.select().filter(Genre.genre_id.in_(genres)).all()
        session.commit()
    albumdata.close()

    return
    print "."
    data = open(os.path.join(dir, "trackData1.txt"))
    for line in data:
        userid, nratings = line.strip().split("|")
        u = User(userid)
        u.add()
        print userid
        for i in range(int(nratings)):
            line = data.next()
            item, score, day, timestamp = line.strip().split("\t")
            hour, minu, sec = timestamp.split(":")
            dt = datetime.datetime.min + datetime.timedelta(int(day))
            dt = dt.replace(hour = int(hour), minute = int(minu), second = int(sec))
            r = Rating(int(item), dt, int(score), u)
            r.add()
            print item, score, dt
        session.flush()
    transaction.commit()
    stop = time.time()
    print "Data read in %d seconds" % (stop -start)

def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("Not enough arguments given")


    metadata.create_all(engine)
    readDatas(args[0])
    print len(list(User.select())), len(list(Rating.select()))
    return 0

if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
