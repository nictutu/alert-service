# alert-service
### Description
Simulates sending a large number of SMS alerts, like for an emergency alert
service. The simulation consists of three parts:
1. A producer that generates a configurable number of messages (default 1000) to random
phone number. Each message contains up to 100 random characters.
2. A sender, who picks up messages from the producer and simulates sending messages by
waiting a random period time distributed around a configurable mean. The sender also
has a configurable failure rate.
3. A progress monitor that displays the following and updates it every N seconds
(configurable):
	1. Number of messages sent so far
	2. Number of messages failed so far
	3. Average time per message so far

One instance each for the producer and the progress monitor will be started while a variable
number of senders can be started with different mean processing time and error rate settings.

### Usage
`alert_service.py` is the simulation. There is an interactive User Input mode and a Demo mode that runs with sample input.<br>
`test_alert_service.py` includes the unit tests I have written to test the functionality included in `alert_service.py`.
