import string, random, time
from multiprocessing import Pool, Queue, Manager
from threading import Timer


class Producer:
	"""Generates a configurable number of messages (default 1000) to a random
	phone number. Each message contains up to 100 random characters."""

	def __init__(self):
		pass

	def generate_message_data(self):
		"""Returns a generated message and phone number"""
		size = random.randint(1,100)
		message = ''.join(random.SystemRandom().choice(string.punctuation + string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(size))
		phone_number = ''.join(random.SystemRandom().choice(string.digits) for _ in range(10))
		return message, phone_number

	def create_message_list(self, message_count=1000):
		"""Takes in a message count and generates and returns all message data"""
		messages = []
		for i in range(message_count):
			messages.append(self.generate_message_data())
		return messages


class Sender:
	"""Picks up messages from the producer and simulates sending messages by
	waiting a random period time distributed around a configurable mean. The
	sender also has a configurable failure rate."""
	def __init__(self, sender_id, mwp, fr):
		self.id = sender_id
		self.mwp = mwp
		self.fr = fr

		self.sent = 0
		self.failed = 0
		self.total_time = 0
		self.avg_time = 0

	def send(self, message):
		"""Takes in a message and waits a random period time distributed around
		a configurable mean. Returns the sender ID and the time taken to send if
		message was sent successfully, otherwise only returns the sender ID."""
		if random.randint(0,100) >= self.fr:
			wait = abs(random.normalvariate(self.mwp, self.mwp/2))
			# print(wait)
			time.sleep(wait)
			return self.id, wait
		else:
			return self.id


class AlertService:
	"""Simulates sending a large number of SMS alerts. Contains a progress monitor
	that displays current number of messages sent/failed and average time per msg."""
	def __init__(self, num_senders, sender_args, progress_interval, num_messages=1000):
		# Configurable Parameters (User input)
		self.num_messages = num_messages
		self.num_senders = num_senders
		self.sender_args = sender_args
		self.progress_interval = progress_interval

		# Generated
		self.messages = []
		m = Manager()
		self.available_senders = m.Queue()
		self.senders = []

		# Progress Stats
		self.messages_sent = 0
		self.messages_failed = 0
		self.total_time = 0
		self.avg_time_per_message = 0

		self.finished = False

	def get_messages(self):
		"""Creates a producer instance and returns the message data."""
		producer = Producer()
		return producer.create_message_list(self.num_messages)

	def send_message(self, message, sender, senders):
		"""Takes in a given message, sender, and queue of senders. Returns the
		result from sending the message and adds the sender into the queue of
		available senders."""
		result = sender.send(message)
		senders.put(sender)
		return result

	def update(self, result):
		"""Is called whenever a sender has finished sending a message. Takes in
		the result of send_message and updates progress statistics accordingly."""
		if type(result) == int:
			self.messages_failed += 1
			self.senders[result].failed += 1
		else:
			self.messages_sent += 1
			self.total_time += result[1]
			self.senders[result[0]].sent += 1
			self.senders[result[0]].total_time += result[1]
			if self.messages_sent == 0:
				self.avg_time_per_message = result[1]
			else:
				self.avg_time_per_message = self.total_time / self.messages_sent
			if self.senders[result[0]].sent == 0:
				self.senders[result[0]].avg_time = result[1]
			else:
				self.senders[result[0]].avg_time = self.senders[result[0]].total_time / self.senders[result[0]].sent

	def progress_display(self):
		"""Displays progress statistics every self.progress_interval seconds
		until service is finished sending messages."""
		# print("Combined Statistics")
		print("Messages sent:    ", self.messages_sent)
		print("Messages failed:  ", self.messages_failed)
		print("Avg time per msg:  {:.2f} seconds".format(self.avg_time_per_message))
		# Code below is for printing stats unique to each sender
		# for sender in self.senders:
		# 	print("Sender #" + str(sender.id+1))
		# 	print("Messages sent:    ", sender.sent)
		# 	print("Messages failed:  ", sender.failed)
		# 	print("Avg Time Per Msg: ", sender.avg_time)
		print("---------------------------------")
		progress_timer = Timer(self.progress_interval, self.progress_display)
		if not self.finished:
			progress_timer.start()
		else:
			progress_timer.cancel()

	def display_errors(self, error):
		"""Is called whenever a sender throws an error/exception. Displays it."""
		print(error)

	def create_senders(self):
		"""Creates sender instances, adds them to an availability queue. Creates a
		Pool of senders to asynchronously send all messages."""
		self.progress_display()
		messages = self.get_messages()
		pool = Pool(self.num_senders)
		for i in range(len(self.sender_args)):
			self.senders.append(Sender(i, self.sender_args[i][0], self.sender_args[i][1]))
			self.available_senders.put(self.senders[i])

		while len(messages) > 0:
			if not self.available_senders.empty():
				sender = self.available_senders.get()
				message = messages.pop(0)
				pool.apply_async(self.send_message, args=(message, sender, self.available_senders), callback=self.update, error_callback=self.display_errors)

		pool.close()
		pool.join()
		self.finished = True
		print("FINISHED")
		return True


def user_input():
	"""Interfaces with the user to input the configurable variables.
	Creates an AlertService instance and returns it."""
	num_messages = int(input("Message Count: "))
	num_senders = int(input("Number of Senders: "))
	sender_args = []
	for i in range(num_senders):
		print("Sender #" + str(i+1))
		mean_wait_period = int(input("Mean Wait Period: "))
		failure_rate = int(input("Failure Rate: "))
		sender_args.append((mean_wait_period, failure_rate))
	progress_interval = int(input("Progress Monitor Interval: "))
	alert_service = AlertService(num_senders, sender_args, progress_interval, num_messages)
	return alert_service


if __name__ == '__main__':
	choice = input("User Input or Demo mode? (Y/N) ").upper()
	if choice == 'Y':  # User Input mode
		# Calls user_input
		user_test = user_input()
		user_test.create_senders()
	elif choice == 'N':  # Demo mode
		# Manually creating an AlertService for testing purposes
		test_service = AlertService(3, [(5, 0), (3, 50), (1, 25)], 5, num_messages=20)
		test_service.create_senders()
