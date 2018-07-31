How to run this example

1. Downlaod the file from [here](https://drive.google.com/open?id=0B0cMxo7fjtlYN0hYSk8tLVpycDQ) 
2. Extract the file in to the project folder and name it `data.csv` ( if the name is something else )

Build & Run the application using the following command
````
docker-compose build
````
````
docker-compose up
```` 
3. To  import the data from `data.csv` go to [https://0.0.0.0:5000/import-data/](https://0.0.0.0:5000/import-data). Alternatively to run the mongodb in debug mode and import the data uncomment the `monogdb()` funtion in the main function()
     
   Note:- For demo purposes when the docker conatiner is build and ran the program starts importing data to mongodb in debug mode and is imported every time you run `docker-compose up`. Comment __mongodb()__ in the __main__ function in app.py. The default username and password have been supplied to mongodb and cab be accessed at [http://0.0.0.0:5000/import-data?username='admin'&password='admin123'](http://0.0.0.0:5000/import-data?username='admin'&password='admin123')which can be found out in the code or docker-compose.yml
2. To know the status of the upload https://0.0.0.0:5000/import-data/<task_id> where you can get the task_id from [https://0.0.0.0:5000/import-data/](https://0.0.0.0:5000/import-data) by going into the header section of the json output
3. Once the upload has completed to know the status of unique users type in the browser [https://0.0.0.0:5000/unique-users](https://0.0.0.0:5000/unique-users) to get the total number of unique users. Always optionally you can type query paremeters to filter the results. Query paremeter takes two parameters `device` and `os`
````
E.G: http://0.0.0.0:5000/unique-users?device=1,2&os=1,2
````
4. TO get the number of lotal users type in the browser [https://0.0.0.0:5000/loyal-users](https://0.0.0.0:5000/loyal-users). It takes the same optional query parameters as unique users i.e `device` and `os`
````
E.G: http://0.0.0.0:5000/loyal-users?device=1,2,3&os=1,3
````