# ---------------------- imports

import sys
import numpy as np

# ---------------------- classes

# for queue
class PriorityQueue:
  def __init__(self):
    # initialise variable
    self.queue = np.empty(100, np.object_)
    self.front = 0
    self.size = 0
    self.max_length = 0

  # check if the queue is empty
  def is_empty(self):
    return self.size == 0

  # add customer to the queue
  def add(self, customer):
    self.queue[self.size] = customer
    self.size += 1

    if self.size > self.max_length:
      self.max_length = self.size

    # sort the queue
    self.insertion_sort()

  # remove customer from the queue
  def remove(self):
    if not self.is_empty():
      removed = self.queue[self.front]
      self.queue[self.front] = None
      self.queue = np.delete(self.queue, self.front, 0)
      tmp = np.empty(1, np.object_)
      np.concatenate((self.queue, tmp))
      self.size -= 1
      return removed
    return

  # sorting method based on priority
  def insertion_sort(self):
    for i in range(1, self.size):
      key = self.queue[i]
      priority = key.priority
      j = i - 1
      while j >= 0 and self.queue[j].priority < priority:
        self.queue[j + 1] = self.queue[j]
        j -= 1

      self.queue[j + 1] = key

    # for i in range(0, self.size):
    #   if self.queue[i] is not None:
    #     print('after sort: ', self.queue[i].arrival_time, self.queue[i].priority)

# for events
class Event:
  def __init__(self, e_type, time, tel_id, customer):
    # initialise variables
    self.e_type = e_type
    self.time = time
    self.tel_id = tel_id
    self.customer = customer

class EventHeap:
  def __init__(self):
    # initialise variables
    self.heap = np.empty(1000, np.object_)
    self.size = 0

  # add new event, e_type is either 'a' (arrival) or 's' (service)
  def add_event(self, e_type, time, tel_id, customer):
    new_event = Event(e_type, time, tel_id, customer)
    # print('new event: ',e_type, time, tel_id, customer.cust_id)

    self.size += 1
    self.heap[self.size - 1] = new_event
    self.sift_up(self.size - 1)

  # sift up operation: swap with its parrent 
  # if the time of pos less than the time of its parrent
  def sift_up(self, pos):
    # get the parent index of pos
    par = (pos - 1) // 2

    if (par >= 0 and self.heap[pos].time < self.heap[par].time):
      tmp = self.heap[par]
      self.heap[par] = self.heap[pos]
      self.heap[pos] = tmp
      self.sift_up(par)

  # check if the heap is empty
  def is_empty(self):
    return self.size == 0

  # get the root of the heap
  def get_min(self):
    removed_e = self.heap[0]
    # swap with the last node
    self.heap[0] = self.heap[self.size - 1]
    self.heap[self.size - 1] = None

    self.size -= 1
    # now the value of the root is greater than its child, so sift down
    self.sift_down(0)
    return removed_e

  # sift down operation: swap with its child 
  # if the time of pos is greater than its child
  def sift_down(self, pos):
    child = pos * 2 + 1

    if child >= self.size:
      return

    if child + 1 < self.size and self.heap[child].time > self.heap[child +1].time:
      child += 1

    if self.heap[pos].time > self.heap[child].time:
      # swap
      tmp = self.heap[pos]
      self.heap[pos] = self.heap[child]
      self.heap[child] = tmp
      self.sift_down(child)

# for tellers
class Tellers:
  class Teller:
    def __init__(self, id):
      # initialise variables
      self.tel_id = id
      self.busy = False
      self.total_customer = 0
      self.service_end = 0
      self.service_time = 0

    # start the service
    def start(self, current_time, customer):
      self.busy = True
      self.total_customer += 1
      self.service_end += (current_time + customer.duration)
      # print('teller ', self.tel_id, 'is serving customer ', customer.cust_id, ' with priority ', customer.priority)

    # end the service
    def end(self, duration):
      self.busy = False
      self.service_time += duration
      # print('service_time', self.service_time)

  def __init__(self, size):
    # initialise variables
    self.size = size
    self.busy_tellers = 0
    self.tellers = []
    # store all tellers in an array
    for i in range(size):
      self.tellers.append(self.Teller(i + 1))
      # print(self.tellers[i].tel_id, self.tellers[i].busy)

  # get an available teller and make it busy
  def add(self):
    self.busy_tellers += 1
    teller = self.tellers[0]
    for tel in self.tellers:
      if (not tel.busy):
        teller = tel
        break
    return teller

  # end the service of the busy teller
  def remove(self, tel_id, duration):
    if self.busy_tellers > 0:
      self.busy_tellers -= 1
    for teller in self.tellers:
      if teller.tel_id == tel_id:
        teller.end(duration)

  # check if there is an available teller
  def is_available(self):
    return self.busy_tellers < self.size

# for customers
class Customer:
  def __init__(self, id, arrival_time, duration, priority):
    # initialise variables
    self.cust_id = id
    self.arrival_time = arrival_time
    self.duration = duration
    self.priority = priority
    self.waiting_time = 0

  # update variable
  def update_waiting_time(self, start_time):
    if start_time > self.arrival_time:
      self.waiting_time += round(start_time - self.arrival_time, 4)
      # print('waiting_time', self.waiting_time)
    return self.waiting_time

# ---------------------- main
def main():
  # read the name of a text file from the console
  user_input = input('Enter filename and total number of tellers: \n')
  user_input = user_input.split()
  
  # initialise variables
  customers = []
  tellers = Tellers(int(user_input[1]))
  events = EventHeap()
  current_time = 0
  total_service_time = 0
  total_simulation_time = 0
  queue = PriorityQueue()
  total_customer = 0
  total_time_queue = 0
  count = 0

  # open and validate the input file
  try:
    file = open(user_input[0])
  except OSError:
    # print an error message on the screen and exit
    print("Error opening file ", user_input[0], ". Program will exit.", sep="")
    return
  
  customer_data = file.readlines()

  # read in the text file line by line
  for i in range(len(customer_data)):
    data = customer_data[i].split()
    if (data[0] == '0'):
      break
    # create new customer
    new_customer = Customer(i + 1, float(data[0]), float(data[1]),
                            int(data[2]))
    # store each customer data
    customers.append(new_customer)
    total_service_time += float(data[1])

  total_customer = len(customers)
  total_service_time = round(total_service_time, 4)

  # initialise the first event for the first customer
  customer = customers[0]
  events.add_event('a', customer.arrival_time, None, customer)
  count += 1

  # continue the loop while the event is not empty
  while not events.is_empty():
    # get the next event
    evt = events.get_min()
    # get the current time
    current_time = evt.time

    # if the event type is arrival, then start the service or queue the customer
    if evt.e_type == 'a':
      # if there is any available teller, serve the customer
      if tellers.is_available():
        # get the available teller
        teller = tellers.add()
        service_end = current_time + evt.customer.duration
        total_time_queue += evt.customer.update_waiting_time(current_time)
        # add new event service
        events.add_event('s', service_end, teller.tel_id, evt.customer)
        # start the service
        teller.start(current_time, evt.customer)
      else:
        queue.add(evt.customer)
    # if the event type is service, then end the service and serve the queue
    else:
      # end the service
      tellers.remove(evt.tel_id,evt.customer.duration)
      # get the next customer from the queue
      next_customer = queue.remove()
      if next_customer:
        # get the available teller
        teller = tellers.add()
        service_end = current_time + next_customer.duration
        total_time_queue += next_customer.update_waiting_time(current_time)
        # add new event service
        events.add_event('s', service_end, teller.tel_id, next_customer)
        # start the service
        teller.start(current_time, evt.customer)

    if count < total_customer:
      # get the next customer data
      customer = customers[count]
      # add new event
      events.add_event('a', customer.arrival_time, None, customer)
      count += 1

  total_simulation_time = round(current_time, 4)

  # report
  print('\nsimulation report ------------------------------------')
  print('number of customers served by each teller: ')
  for server in tellers.tellers:
    print('teller ', server.tel_id, ' | ', server.total_customer)

  print('total simulation time: ', total_simulation_time)

  print('average service time per customer:',
        round(total_service_time / total_customer, 4))

  print('average waiting time per customer:',
        round(total_time_queue / total_customer, 4))

  print('maximum length of the queue:', queue.max_length)

  print('average length of the queue:',
        round(total_time_queue / total_simulation_time, 4))

  print('idle rate of each teller: ')
  for teller in tellers.tellers:
    idle_time = abs(total_simulation_time-teller.service_time)
    print('teller ', teller.tel_id, ' | ',
          round(idle_time/total_simulation_time, 4))

  print('--------------------------------------------------------')
  print('\n\n')
  return

# ---------------------- execute main
if __name__ == "__main__":
  sys.exit(main())
