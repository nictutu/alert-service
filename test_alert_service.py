import unittest
import alert_service


class TestProducer(unittest.TestCase):
	"""Creates a Producer instance and tests its functionality."""
	def setUp(self):
		self.prod = alert_service.Producer()

	def test_single_message(self):
		"""Uses generate_message_data to generate a single message/phone_number."""
		message, phone_number = self.prod.generate_message_data()
		self.assertEqual(type(message), str)
		self.assertLessEqual(len(message), 100)
		self.assertEqual(type(phone_number), str)
		self.assertEqual(len(phone_number), 10)

	def test_messages(self):
		"""Uses create_message_list to generate all message data, using default
		value of 1000 for message_count."""
		messages = self.prod.create_message_list()
		self.assertEqual(len(messages), 1000)


class TestSender(unittest.TestCase):
	"""Creates a Sender instance and tests its functionality."""
	def setUp(self):
		self.sender_id = 0
		self.mean_wait_period = 5
		self.failure_rate = 20
		self.sender = alert_service.Sender(self.sender_id, self.mean_wait_period, self.failure_rate)

	def test_send_message(self):
		"""Uses send_message to send a single message."""
		message = "Hello!"
		result = self.sender.send(message)
		self.assertIsNotNone(result)
		if type(result) == int:
			self.assertEqual(result, self.sender_id)
		else:
			self.assertEqual(result[0], self.sender_id)


class TestAlertService(unittest.TestCase):
	"""Tests the functionality of the AlertService."""
	def setUp(self):
		self.num_senders = 3
		self.sender_args = [(1, 10), (3, 20), (5, 30)]
		self.progress_interval = 5
		self.num_messages = 20
		self.alert_serv = alert_service.AlertService(self.num_senders, self.sender_args, self.progress_interval, self.num_messages)

	def test_get_messages(self):
		"""Uses get_messages to get all message data."""
		messages = self.alert_serv.get_messages()
		message_example, phone_number_example = messages[0]
		self.assertEqual(len(messages), self.num_messages)
		self.assertEqual(type(message_example), str)
		self.assertLessEqual(len(message_example), 100)
		self.assertEqual(type(phone_number_example), str)
		self.assertEqual(len(phone_number_example), 10)

	def test_send_message(self):
		"""Creates a single sender and uses send_message to send a single message."""
		message = "Hello!"
		sender_id = 0
		mean_wait_period = 5
		failure_rate = 20
		sender = alert_service.Sender(sender_id, mean_wait_period, failure_rate)
		available_senders = self.alert_serv.available_senders
		result = self.alert_serv.send_message(message, sender, available_senders)
		self.assertIsNotNone(result)

	def test_multiple_senders(self):
		"""Uses create_senders to create multiple senders and sends the entire
		list of messages."""
		self.assertTrue(self.alert_serv.create_senders())
		self.assertEqual(len(self.alert_serv.senders), self.num_senders)
		processed_msgs = self.alert_serv.messages_sent + self.alert_serv.messages_failed
		self.assertEqual(processed_msgs, self.num_messages)


if __name__ == '__main__':
	unittest.main()
