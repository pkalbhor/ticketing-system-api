import json
import pickle
from filelock import FileLock
from flask import request
from flask_restful import Resource, abort

class CreateTicketAPI(Resource):
  """
  Endpoint for creating a ticket
  """
  def post(self):
    """POST method for creating a ticket"""
    data = request.data
    json_data = validate_data(data)
    response = create_ticket(json_data)
    return response, 201

class GetListOfTicketsAPI(Resource):
  """
  Endpoint for getting a list of tickets
  """
  def get(self):
    """Returns list of tickets available in a system"""
    response = get_ticket_list()
    return response, 200

class GetListOfAssignee(Resource):
  """
  Endpoint for getting a list of people to whom we assign tickets
  """
  def get(self):
    """Returns list of people saved as a sample"""
    users_datafile = 'data/sample_users_data.pickle'
    with FileLock(users_datafile+'.lock'):
      with open(users_datafile, 'rb') as f:
        users = pickle.load(f)
        f.close()
    response = {
      'message': 'List of assignee fetched',
      'success': True,
      'data'   : list(users.values())
      }
    return response, 200

def get_ticket_list():
  """Returns list of tickets after fetching from file"""
  data = []
  with open('data/tickets.pickle', 'rb') as f:
    try:
      while True:
        data.append(pickle.load(f))
    except EOFError:
      f.close()
  return {
    'message': 'List of tickets fetched',
    'success': True,
    'data'   : data
  }

def validate_data(data):
  """
  Validate data and return appropriate response
  """
  # Making sure that provided data is of JSON format
  try:
    json_data = json.loads(data.decode('utf-8'))
  except: 
    abort(400,
      message = "Bad request! Expected content to be in JSON format",
      success = False)
  
  # Making sure input data has correct keys
  if not set(['user_id', 'issue']).issubset(json_data):
    abort(400,
      message = "Bad request! Expected following keys in a data: 'user_id', 'issue' ",
      success = False)

  # Here custom validators could be added to verify user_id and issue
  if not (json_data.get('user_id').strip() and json_data.get('issue').strip()):
    abort(400,
      message = "Bad request! 'user_id' or 'issue' field can not be empty",
      success = False)

  return json_data
    
def create_ticket(json_data):
  """Create ticket format, assign and save it"""
  user_id = json_data.get('user_id')
  issue = json_data.get('issue')
  ticket = {
            'ticket_id': 'to be decided',
            'issue'    : issue,
            'assigned_to': 'Not assigned',
            'raised_by'  : user_id,
            }
  ticket = assign_and_save_ticket(ticket)
  return {
          'message': 'Ticket created successfully',
          'success': True,
          'data'   : {
            'ticket_id': ticket.get('ticket_id'),
            'assigned_to': ticket.get('assigned_to')
           }
         }

def assign_and_save_ticket(ticket):
  """Assign ticket to a representative and save it"""

  users_datafile = 'data/sample_users_data.pickle'

  with FileLock(users_datafile+'.lock'):
    users_data = None
    with open(users_datafile, "rb") as f:
      users_data = pickle.load(f)
      f.close()

    # Get possible assignee, ticket_id for a ticket
    assigned_to, ticket_id = implement_round_robin()

    # Assign ticket
    users_data[str(assigned_to)].get('tickets').append(ticket_id)

    # Write users data
    with open(users_datafile, "wb") as f:
      pickle.dump(users_data, f)
      f.close()

    ticket['ticket_id'] = str(ticket_id)
    ticket['assigned_to'] = str(assigned_to)

    # Save tickets
    with open('data/tickets.pickle', 'ab+') as f:
      pickle.dump(ticket, f)
      f.close()
    return ticket

def implement_round_robin():
  """Assign tickets to users by taking turns"""
  datafile = 'data/round_robin_turn.pickle'
  with open(datafile, "rb") as f:
    data = pickle.load(f)
    assigned_to = data.get('assigned_to')
    ticket_id = data.get('ticket_id')
    total_users = data.get('total_users')
    f.close()

  new_assigned_to = assigned_to+1 if assigned_to < total_users else 1
  with open(datafile, "wb") as f:
    pickle.dump({
      'ticket_id': ticket_id+1,
      'assigned_to': new_assigned_to,
      'total_users': total_users
      }, f)
    f.close()

  return (assigned_to, ticket_id)