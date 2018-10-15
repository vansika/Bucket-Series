# Bucket Series

Ever missed an episode of your favorite TV show? Not anymore! Bucket Series is a
program that tells you when the next episodes of your favorite TV shows are airing.

We use [IMDb](https://imdb.com) for TV Show data.

## Setup

Create the MySQL database. You need to install MySQL on your computer for this. See
how to install MySQL [here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/).

Then create the database to store TV show data locally using the following commands

```
$ source create_database.sql
```

After this, you need to install the python bindings we use for fetching IMDb data.

```
$ pip install imdbpy
```
Insatll mysql-connector to let python interact with database.

```
$ pip install mysql-connector-python
```

Then, input correct values into `config.py` for database host, user name, password,
database name, email host, email port, sender email and password.


## Running the script

Now just run the script and input your email address and favourite TV shows and let the
script run its magic!

```
$ python series_info.py
```

# Examples

You can input a single TV show or multiple TV shows, if you want. Some examples are as follows:

```
$ python series_info.py
Email: myemail@gmail.com
Series: Game of Thrones


$ python series_info.py
Email: myemail@gmail.com
Series: Game of Thrones, Rick and Morty, Friends
```
# Improvments

Users can be provided with streaming dates of TV series that come under the same genre or
cast same actors as provided by the user in the input.

# License

```
Copyright 2018 Vansika Pareek

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in the 
Software without restriction, including without limitation the rights to use, copy, 
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the 
following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
```
