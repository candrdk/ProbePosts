# ProbePosts
Microblogging for UFO hunters.

TODO: longer description

![Screenshot of the ProbePosts home page](screenshot.png)

# How to run
Clone the repository and run the following command to install the required packages (preferably in a venv):
```
$ pip install -r requirements.txt
```
Create a new database in pgAdmin (preferably named ProbePosts) and add the following to an `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ProbePosts
DB_USERNAME=postgres
DB_PASSWORD=postgres
```
If these default values don't match your setup (you might for example have a different password), modify the `.env` as needed.

To fill the database with data, run the `init_db.py` script:
```
$ py ./data/init_db.py
```
This will fill the data from the `/data/tables/` csv files into their corresponding tables in the postgres database specified in the `.env` file. For more on how these csv files were generated, see the 'Generating datasets' section.

The server can then be started with:
```
$ flask run
```
ProbePosts should then be available at https://localhost:5000/

## Generating datasets
The raw UFO sightings dataset we are using for this project can be found in `/data/raw/dataset_raw.csv`. The dataset is a scrape of UFO sighting reports from https://nuforc.org and is publically available on [Kaggle](https://www.kaggle.com/datasets/joebeachcapital/ufo-sightings/data). Since image urls are not included in the dataset, we scrape them ourselves from [nuforc](https://nuforc.org) using the `/data/raw/scrape_image_urls.py` script, which will generate `/data/raw/image_urls_raw.csv`.

> Scraping these images takes a *long* time. You shouldn't have to touch or run any of the files in `/data/raw/` unless you want to significantly alter the structure of the database.

We have then cleaned this dataset up using the `/data/raw/clean_dataset.py` script, which takes the `dataset_raw.csv` and `image_urls_raw.csv` files and filters out reports with non-image attachments or image links that 404. This is the script that was used to generate the `dataset.csv` and `image_urls.csv` files found in `/data/`. The `/data/init_db.py` script will later combine these files to give the posts their proper image urls when they are inserted into the database. If an image url for a post is missing in the `image_urls.csv` file (or if the file is empty), posts are just assigned a dummy image from https://picsum.photos/512.

Using the cleaned dataset, the tables used by ProbePosts can be generated by running the `/data/generate_tables.py` script:
```
$ py ./data/generate_tables.py
```
This will generate csv files for posts, users, follow relationships, etc in the `/data/tables/` folder. Note that users, ratings and follows are randomly generated.
