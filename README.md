# ProbePosts
Microblogging for UFO hunters.

# How to run
To run ProbePosts, run the following command from the root of the repository:
```
$ flask run
```
This will start a server on localhost port 5000, which you can view in the browser using the following URL: https://localost:5000/

## Set up a virtual environment
> This walkthrough assumes you are running on linux, mac or git bash on windows. Commands will differ slightly on `cmd` and `powershell`.

First navigate to the root of the repository and create a virtual environment by running:
```
$ python3 -m venv venv
```
You can then enter the virtual environment by running:
```
$ source venv/Scripts/activate
```
You can then install all PropePosts dependencies in this virtual environment by running
```
$ pip install -r requirements.txt
```
