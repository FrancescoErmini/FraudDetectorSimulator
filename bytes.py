import sys
import cPickle
import hashlib

def bytes(jsonObj):
	JSON_as_string = cPickle.dumps(jsonObj)
	return sys.getsizeof(JSON_as_string)


def main():

	

	originJSON = {
	"id": hashlib.sha256("called number and other infos").hexdigest(),
	"origin": "sip:212630560855@195.81.140.216",
	"termin": "sip:42788236970593@195.81.140.216:5067",
	"transit": "sip:212630560855@sipgw5063.com",
	"timestamp": 1540420525.877242000,
	"duration": 20.995604000,
	"lrn":  571434,
	"cid": "3F16BABC-5BD0F398000D866E-7CF49700@phonegroup",
	"terminrate": 20
	}

	terminJSON = {
	"id": hashlib.sha256("called number and other infos").hexdigest(),
	"duration": 20.995604000,
	"lrn":  571434,
	"cid": "3F16BABC-5BD0F398000D866E-7CF49700@phonegroup",
	"terminrate": 20
	}

	transitJSON = {
	"id": hashlib.sha256("called number and other infos").hexdigest(),
	"transit": "sip:212630560855@sipgw5063.com"
	}

	print("origin:", bytes(originJSON))
	print("termin:", bytes(terminJSON))
	print("transit:", bytes(transitJSON))



	n_intermidiaries = 4
	global_minutes_year = 30*(10**9)
	locale_minutes_year= 884898390#100*(10**6)
	minute_per_year = 60*24*365
	call_minute_average = 10

	global_calls_year = global_minutes_year / call_minute_average
	global_calls_day = global_calls_year / 365
	global_calls_hour = global_calls_day / 24
	global_calls_minute = global_calls_hour / 60

	local_calls_year = locale_minutes_year / call_minute_average
	local_calls_day = local_calls_year / 365
	local_calls_hour = local_calls_day / 24
	local_calls_minute = local_calls_hour / 60

	print("local call minute" + str(local_calls_minute))

	megabyte = 10**6

	bytes_per_call = bytes(originJSON)+bytes(terminJSON)+n_intermidiaries*bytes(transitJSON)
	print("kbytes", float(bytes_per_call)/(10**3))
	# 23,551,832

	#bilion_minutes_year = 15,048,355,630
	#				          884,898,390


	#n_calls = (bilion_minutes_year / minute_per_year) / call_minute_average
	'''
	print("global call", global_calls_day)
	print("gigabytes day:",  (global_calls_day*()/(10.0**9)))
	'''
	print("local number of call in one day", local_calls_day)
	print("x-byte in one day:",  (local_calls_day*bytes(originJSON)+bytes(terminJSON)+n_intermidiaries*bytes(transitJSON))/megabyte )


if __name__== "__main__":
  main()



