class base():

	def __init__(self):
		self.user_prefs = {}

	def fetch_user_prefs(self):
		return

	def transform(array):

		transformed_array = {}

		for user in array:
			for problem in user:
				transformed_array[problem][user] = array[user][problem]

		return transformed_array