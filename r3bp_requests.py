"""
Get data from NASA R3BP database using API
"""

import requests
import json



def get(savepath, body1="sun", body2="earth", family="halo", libr="2", branch="S"):
	"""Query periodic orbit family data
	"""
	dict_res = requests.get(
		"https://ssd-api.jpl.nasa.gov/periodic_orbits.api?sys="+body1+"-"+body2+"&family="+family+"&libr="+libr#+"&branch="+branch
	).json()
	# write to file
	file = open(savepath, 'wt')
	file.write(json.dumps(dict_res, indent=4, sort_keys=False))
	file.close()
	print(f"Saved to file: {savepath}")
	return


if __name__=="__main__":
	get(
		savepath="./sun_earth_l2_haloS.json",
		body1="sun",
	)