# DEAssessment

This bundle contains the results of the DE assessment.
The `explore.ipynb` notebook contains some exploratory work and is not needed for the app.
The code and data for the app can be found in the `localapp` folder.

## Prerequisites
In order to run the app locally using docker&docker-compose, the following should be installed:
 - docker==20.10.12
 - docker-compose==1.25


## How to run locally

Build the app locally:
`docker build -t localapp .`

Once the build has finished, start the components (app and database):
`docker-compose up`

_Note_: the app does not wait for the db to finish initializing before starting. If db is not up and running, it might log errors on db write.

Access the app using the url output:
`
localapp    |   You can now view your Streamlit app in your browser.
localapp    | 
localapp    |   URL: http://0.0.0.0:8501
`

Check that the data is loaded to db:
`docker exec -it mysqldb mysql -utest_user -ptestpasswd`
`mysql> use shipping;`
`mysql> select count(*) from route_weather;`


Alternative to docker&docker-compose (app only, no database):

1. create virtual environment and install requirements.txt
2. start app using `streamlit run localapp/main.py`

_Note_: this will not run the db load, the app will log an error message:
```
 Could not write to db. Error: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on '10.5.0.5' ([Errno 113] No route to host)")
(Background on this error at: https://sqlalche.me/e/14/e3q8)

```
or check out the deployed visulization:

https://elena-elena-deassessment-localappmain-m9q45h.streamlit.app/

## Tests

To run the tests pytest==6.0.1 should be installed.
Run the tests by using `pytest` command. This will run the tests defined in test folder.
