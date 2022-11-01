import os
import pickle
from flask import Flask, render_template
from flask_restful import Api
from api.ticket_api import CreateTicketAPI

def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Adding API endpoints
    api.add_resource(CreateTicketAPI, '/ticket')

    # Do something only once before very first request
    @app.before_first_request
    def before_first_request():
        """Create and save sample data in a file"""
        os.system('mkdir -p data')
        users_datafile = 'data/sample_users_data.pickle'
        if os.path.exists(users_datafile):
            with open(users_datafile, "rb") as f:
                sample_data = pickle.load(f)
                f.close()
                if len(sample_data) < 5:
                    print('Will be creating new data')
                else:
                    print('Users data already exists')
                    return
        sample_data = {
                       '1': {'id': '1', 'name': 'Ravi', 'tickets': []},
                       '2': {'id': '2', 'name': 'Kiran', 'tickets': []},
                       '3': {'id': '3', 'name': 'Sameer', 'tickets': []},
                       '4': {'id': '4', 'name': 'Murugan', 'tickets': []},
                       '5': {'id': '5', 'name': 'Vanita', 'tickets': []},
                      }
        data = pickle.dumps(sample_data)
        with open(users_datafile, "wb") as f:
            pickle.dump(sample_data, f)
            f.close()
        with open('data/round_robin_turn.pickle', "wb") as f:
            pickle.dump({'ticket_id': 1, 'assigned_to': 1, 'total_users': 5}, f)
            f.close()

    @app.route('/', defaults={'_path': ''})
    @app.route('/<path:_path>')
    def api_documentation(_path):
        """
        Endpoint for API documentation HTML
        """
        docs = {}
        for endpoint, view in app.view_functions.items():
            view_class = dict(view.__dict__).get('view_class')
            if view_class is None:
                continue

            class_name = view_class.__name__
            class_doc = view_class.__doc__.strip()
            urls = sorted([r.rule for r in app.url_map._rules_by_endpoint[endpoint]])
            category = 'API'
            if category not in docs:
                docs[category] = {}

            docs[category][class_name] = {'doc': class_doc, 'urls': urls, 'methods': {}}
            for method_name in view_class.methods:
                method = view_class.__dict__.get(method_name.lower())
                method_dict = {'doc': method.__doc__.strip()}
                docs[category][class_name]['methods'][method_name] = method_dict
                if hasattr(method, '__role__'):
                    method_dict['role'] = getattr(method, '__role__')

        return render_template('api_documentation.html.Jinja', docs=docs)

    return app