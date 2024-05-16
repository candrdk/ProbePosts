DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS States;
DROP TABLE IF EXISTS Cities;
DROP TABLE IF EXISTS Countries;

CREATE TABLE Countries(
    country_name VARCHAR(64) PRIMARY KEY
);

INSERT INTO Countries(country_name) VALUES ('United States');

CREATE TABLE Cities(
    id INTEGER PRIMARY KEY,
    city_name VARCHAR(64) NOT NULL
);

CREATE TABLE States(
    id INTEGER PRIMARY KEY,
    state_name VARCHAR(64) NOT NULL
);

CREATE TABLE Users(
    id INTEGER PRIMARY KEY, 
    username VARCHAR(32) UNIQUE NOT NULL, 
    password_hash VARCHAR(256) NOT NULL, 
    country VARCHAR(32) NOT NULL REFERENCES Countries(country_name), 
    state_id INTEGER REFERENCES States(id),
    city_id INTEGER REFERENCES Cities(id)
);

CREATE TABLE Posts(
    id SERIAL PRIMARY KEY,
    poster_id INTEGER NOT NULL REFERENCES Users(id),
    post_date DATE NOT NULL,
    sighting_date DATE NOT NULL,
    sighting_time TIME NOT NULL,
    country VARCHAR(64) NOT NULL REFERENCES Countries(country_name),
    state_id INTEGER REFERENCES States(id),
    city_id INTEGER REFERENCES Cities(id),
    duration VARCHAR(128) NOT NULL,
    summary VARCHAR(512) NOT NULL,
    image_url VARCHAR(512),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);
