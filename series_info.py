import mysql.connector
from mysql.connector import errorcode
import imdb
import itertools
from datetime import date
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import config

message = " "

dic_months = {'Jan.' : 1, 'Feb.' : 2, 'Mar.' : 3, 'Apr.' : 4, 'May' : 5, 'Jun.' : 6, 'Jul.' : 7, 'Aug.' : 8, 'Sep.' : 9, 'Oct.' : 10, 'Nov.' : 11, 'Dec.' : 12}

def episode_message(name, date):
	global message
	message = message + "TV series name: {}" .format(name) + "\n" + "Status: The next episode airs on {}." .format(date) + "\n" + "\n"
	
def season_message(name, date):
	global message
	message = message + "TV series name: {}" .format(name) + "\n" + "Status: The next season begins in {}." .format(date) + "\n" + "\n"

def noinfo_message(name):
	global message
	message = message + "TV series name: {}" .format(name) + "\n" + "Status: No further information available." + "\n" + "\n"
	
def error_message(name):
	global message
	message = message + "TV series name: {}" .format(name) + "\n" + "Status: No TV series with this name exists" + "\n" + "\n"

def streamed_message(name):
	global message
	message = message + "TV series name: {}" .format(name) + "\n" + "Status: The show has finished streaming all its episodes" + "\n" + "\n"

def check_if_already_streamed(ia, tvshow):
	"""called to check if the TV series have stopped streaming or not.
	If so, get_dates() function would not be called since there 
	are no dates to retrieve.

	Args:
		tv_show (imdb.Movie object): the search result after searching for name on IMDb
		ia (imdb object): used to extract info from imdb

	"""
	ia.update(tvshow, 'main')
	streamed_years = tvshow['series years']
	if streamed_years[-1] == '-':
		return False
	else:
		return True

def create_object(name, ia):
	"""Returns the first matching TV series object with the name.
	If none exists, an empty list is returned

	Args:
		name (str): the name of the tv show
		ia (imdb object): used to extract info from imdb
	"""
	search_result = ia.search_movie(name)
	search_tvseries = itertools.ifilter(lambda s : s['kind'] == 'tv series', search_result)
	search_tvseries = list(itertools.islice(search_tvseries, 1))
	return search_tvseries

def get_dates(name, ia, tvshow):
	"""Returns the date of the first episode that will be aired after the current day.
	If no info on IMDb, function returns None.

	Args:
		name (str): the name of the tv show
		ia (imdb object): used to extract info from imdb
		tv_show (imdb.Movie object): the search result after searching for name on IMDb

		IMDb returns date in the following formats: [10 Aug. 2018], [Aug. 2018] and [2018]
		to compare with python's current date (2018-08-10), IMDb and python dates have been 
		broken.
	"""
	ia.update(tvshow, 'episodes')
	today = date.today()
	date_today = [today.day, today.month, today.year]
	if not tvshow.has_key('episodes'):
		noinfo_message(name)
		return None
	else:
		for season in sorted(tvshow['episodes']):
			episode = len(tvshow['episodes'][season])
			for i in range(1, episode + 1):
				if i in tvshow['episodes'][season]:
					if tvshow['episodes'][season][i].has_key('original air date'):
						date_series = [x for x in tvshow['episodes'][season][i]['original air date'].split(" ")]
						if len(date_series) == 3:
							date_series[1] = dic_months[date_series[1]]
							date_series = [int(x) for x in date_series]
							date_formatted = str(date_series[2]) + "-" + str(date_series[1]) + "-" + str(date_series[0])
							if date_series[2] > date_today[2]:
								return date_formatted
							elif date_series[2] < date_today[2]:
								continue
							else:
								if date_series[1] > date_today[1]:
									return date_formatted
								if date_series[1] < date_today[1]:
									continue
								else:
									if date_series[0] > date_today[0]:
										return date_formatted
									elif date_series[0] < date_series[0]:
										continue
									else:
										return date_formatted
						elif len(date_series) == 2:
							date_series[0] = dic_months[date_series[0]]
							date_series = [int(x) for x in date_series]
							date_formatted = str(date_series[1]) + "-" + str(date_series[0])
							if date_series[1] > date_today[2]:
								return date_formatted
							elif date_series[1] < date_today[2]:
								continue
							else:
								if date_series[0] >= date_today[1]:
									return date_formatted
								else:
									continue
							noinfo_message(name)
						else:
							if int(date_series[0]) >= date_today[2]:
								return tvshow['episodes'][season][i]['original air date']
							else:
								continue
					else:
						noinfo_message(name)
						return None
				else:
					continue
		noinfo_message(name)
		return None
	
def update_series(name, ia, cursor):
	"""called if name of series already exists in database.
	if current date is greater than stored date, then next streaming episode
	is found out. The possibility that the series have finished streaming is also 
	checked.

	Args:
		name (str): the name of the tv show
		ia (imdb object): used to extract info from imdb
		cursor : cursor object
	"""
	sql = "select next_episode, next_season from tvshow where name = %s"
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	today = date.today()
	date_today = [today.day, today.month, today.year]
	if result[0] == None or result[0] == "NULL":
		search_tvseries = create_object(name, ia)
		tvshow = search_tvseries[0]
		status = check_if_already_streamed(ia, tvshow)
		if status:
			sql = "update tvshow set next_episode = %s where name = %s"
			value = ("not alive",name)
			cursor.execute(sql, value)
			streamed_message(name)
		else:
			if result[1] != "NULL":
				if result[1] <= date_today[2]:
					next_date_of_series = get_dates(name, ia, tvshow)
					if not next_date_of_series:
						noinfo_message(name)
						return
					elif len(next_date_of_series) == 4:
						sql = "update tvshow set next_season = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						season_message(name, next_date_of_series)
					else:
						sql = "update tvshow set next_episode = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						episode_message(name, next_date_of_series)
				else:
					season_message(name, result[1])
			else:
				noinfo_message(name)
	elif result[0] == 'not alive':
		streamed_message(name)
		return
	else:
		date_series = [int(x) for x in result[0].split("-")]
		if len(date_series) == 3:
			if (date_today[2] > date_series[2]) or ((date_today[2] == date_series[2]) and (date_today[1] > date_series[1])) or ((date_today[2] == date_series[2]) and (date_today[1] == date_series[1]) and (date_today[0] > date_series[0])):
				search_tvseries = create_object(name, ia)
				tvshow = search_tvseries[0]
				status = check_if_already_streamed(ia, tvshow)
				if status:
					sql = "update tvshow set next_episode = %s where name = %s"
					value = ("not alive",name)
					cursor.execute(sql, value)
					streamed_message(name)
				else:
					next_date_of_series = get_dates(name, ia, tvshow)
					if not next_date_of_series:
						sql = "update tvshow set next_season = %s, next_episode = %s where name = %s"
						value = ("NULL", "NULL",name)
						noinfo_message(name)
					elif len(next_date_of_series) == 4:
						sql = "update tvshow set next_season = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						season_message(name, next_date_of_series)
					else:
						sql = "update tvshow set next_episode = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						episode_message(name, next_date_of_series)
			else:
				episode_message(name, result[0])
		else:
			if ((date_today[1] > date_series[1]) or ((date_today[1] == date_series[1]) and (date_today[0] > date_series[0]))):
				search_tvseries = create_object(name, ia)
				tvshow = search_tvseries[0]
				status = check_if_already_streamed(ia, tvshow)
				if status:
					sql = "update tvshow set next_episode = %s where name = %s"
					value = ("not alive",name)
					cursor.execute(sql, value)
					streamed_message(name)
				else:
					next_date_of_series = get_dates(name, ia, tvshow)
					if not next_date_of_series:
						sql = "update tvshow set next_season = %s, next_episode = %s where name = %s"
						value = ("NULL", "NULL",name)
						cursor.execute(sql, value)
						noinfo_message(name)
					elif len(next_date_of_series) == 4:
						sql = "update tvshow set next_season = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						season_message(name, next_date_of_series)
					else:
						sql = "update tvshow set next_episode = %s where name = %s"
						value = (next_date_of_series,name)
						cursor.execute(sql, value)
						episode_message(name, next_date_of_series)
			else:
				episode_message(name, result[0])

def get_show(name, cursor):
	"""returns None if TV series name does not exists in
	database 

	Args:
		name: name of TV series
		cursor: cursor object
	"""
	sql = "select id from tvshow where name = %s"
	cursor.execute(sql, (name,))
	result = cursor.fetchone()
	if result == None:
		return None
	else:
		return result[0]

def insert(name, ia, tvshow, cursor):
	"""called if name of TV series does not exists in the
	database. Inserts next streaming date in the database after
	checking if the serie has finished streaming or not.

	Args:
		name (str): the name of the tv show
		ia (imdb object): used to extract info from imdb
		tv_show (imdb.Movie object): the search result after searching for name on IMDb
		cursor: cursor object
	"""
	sql = "insert into tvshow (name) values (%s)" 
	cursor.execute(sql, (name,))
	status = check_if_already_streamed(ia, tvshow)
	if status:
			sql = "update tvshow set next_episode = %s where name = %s"
			value = ("not alive",name)
			cursor.execute(sql, value)
			streamed_message(name)
	else:
		next_date_of_series = get_dates(name, ia, tvshow)
		if next_date_of_series:
			if len(next_date_of_series) == 4:
				sql = "update tvshow set next_season = %s where name = %s"
				value = (next_date_of_series,name)
				cursor.execute(sql, value)
				season_message(name, next_date_of_series)
			else:
				sql = "update tvshow set next_episode = %s where name = %s"
				value = (next_date_of_series,name)
				cursor.execute(sql, value)
				episode_message(name, next_date_of_series)
		else:
			return

db = mysql.connector.connect(
	host = config.DATABASE_HOST,
	user = config.DATABASE_USER,
	password = config.DATABASE_PASSWORD,
	database = config.DATABASE_NAME
)

def send_mail(mail, message):
	"""Sends email to users with a valid email id

	Args:
		mail: E-mail id of user
		message: text message to deliver
	"""
	sender = config.EMAIL_SENDER
	receivers = mail
	msg = MIMEMultipart()
	msg['From'] = "Bucket Series"
	msg['To'] = receivers
	msg['Subject'] = "Schedule of your favorite TV series"
	msg.attach(MIMEText(message, 'plain'))

	try:
		smtpObj = smtplib.SMTP(host = config.EMAIL_HOST, port = config.EMAIL_PORT)
		smtpObj.ehlo()
		smtpObj.starttls()
		smtpObj.ehlo()
		smtpObj.login(sender,config.EMAIL_PASSWORD)
		text = msg.as_string()
		smtpObj.sendmail(sender, receivers, text)    

	except smtplib.socket.error as e:
			logging.error ("Could not connect to " + serverHost + ":" + cliCfg.find('serverport').text + " - is it listening / up?")  
	except:
		print "Invalid Email"

def main(show_list, mail):
	"""Iteratively updates/stores next streaming date of
	list of TV series

	Args:
		show_list : list of TV series
		mail: E-mail id of user
	"""
	ia = imdb.IMDb()
	cursor = db.cursor()
	for name in show_list:
		name = name.strip()
		if not name:
			print "Input not provided"
			return
		if not get_show(name, cursor): 
			search_tvseries = create_object(name, ia)
			if not search_tvseries:
				error_message(name)
			else:
				tvshow = search_tvseries[0]
				insert(name, ia, tvshow, cursor)
		else:
			update_series(name, ia, cursor)

	cursor.close()
	db.commit()
	send_mail(mail, message)
	
mail = raw_input("Email: ")
show_name = raw_input("Series: ")

show_list = [x for x in show_name.split(",")]
main(show_list, mail)

db.close()
