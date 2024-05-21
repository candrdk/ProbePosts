DROP TABLE IF EXISTS Ratings;
DROP TABLE IF EXISTS Follows;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS States;
DROP TABLE IF EXISTS Cities;

CREATE TABLE States(
    state_code CHAR(2) PRIMARY KEY,
    state_name VARCHAR(64) NOT NULL
);

CREATE TABLE Cities(
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE Users(
    id SERIAL PRIMARY KEY,
    display_name VARCHAR(64) NOT NULL,
    handle VARCHAR(32) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    state_code CHAR(2) REFERENCES States(state_code),
    city_id INTEGER REFERENCES Cities(id)
);

CREATE TABLE Posts(
    id SERIAL PRIMARY KEY,
    poster_id INTEGER NOT NULL REFERENCES Users(id),
    post_date DATE NOT NULL,
    sighting_date DATE NOT NULL,
    sighting_time TIME NOT NULL,
    state_code CHAR(2) REFERENCES States(state_code),
    city_id INTEGER REFERENCES Cities(id),
    duration VARCHAR(128) NOT NULL,
    summary VARCHAR(512) NOT NULL,
    image_url VARCHAR(512),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE TABLE Follows(
    user_id INTEGER REFERENCES Users(id),
    follows_id INTEGER REFERENCES Users(id),
    PRIMARY KEY (user_id, follows_id)
);

CREATE TABLE Ratings(
    user_id INTEGER REFERENCES Users(id),
    post_id INTEGER REFERENCES Posts(id),
    rating BOOLEAN NOT NULL,
    PRIMARY KEY (user_id, post_id)
);
