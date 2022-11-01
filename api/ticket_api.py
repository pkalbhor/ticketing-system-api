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

  users_datafile = 'sample_users_data.pickle'

  with FileLock(users_datafile+'.lock'):
    users_data = None
    with open(users_datafile, "rb") as f:
      users_data = pickle.load(f)
      f.close()

    # Get possible assignee for a ticket
    assigned_to, ticket_id = implement_round_robin()

    # Assign ticket
    users_data[str(assigned_to)].get('tickets').append(ticket_id)

    # Write users data
    with open(users_datafile, "wb") as f:
      pickle.dump(users_data, f)
      f.close()

    ticket['ticket_id'] = ticket_id
    ticket['assigned_to'] = assigned_to
    return ticket

def implement_round_robin():
  with open('round_robin_turn.pickle', "rb") as f:
    data = pickle.load(f)
    assigned_to = data.get('assigned_to')
    ticket_id = data.get('ticket_id')
    total_users = data.get('total_users')
    f.close()

  new_assigned_to = assigned_to+1 if assigned_to < total_users else 1
  with open('round_robin_turn.pickle', "wb") as f:
    pickle.dump({
      'ticket_id': ticket_id+1,
      'assigned_to': new_assigned_to,
      'total_users': total_users
      }, f)
    f.close()

  return (assigned_to, ticket_id)