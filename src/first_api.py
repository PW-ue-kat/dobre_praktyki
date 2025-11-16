# 1. Import the Flask class from the flask module
from flask import Flask

# 2. Create an instance of the Flask class.
# __name__ is a special variable in Python that holds the name of the current module.
# Flask uses this to know where to look for resources like templates and static files.
app = Flask(__name__)

# 3. Define a route using a decorator.
# This tells Flask that the function below should be triggered
# when someone accesses the root URL ('/') of the server.
@app.route('/')
def hello_world():
    """
    This function runs when the '/' route is accessed.
    It returns the string "Hello, World!" which will be
    displayed in the user's web browser.
    """
    return 'Hello, World!'

# 4. Check if the script is being run directly.
# This ensures that the server only runs when you execute the script
# with `python app.py`, not when it's imported as a module.
if __name__ == '__main__':
    # 5. Run the application.
    # debug=True enables the built-in debugger and auto-reloader,
    # which is very helpful during development.
    # host='0.0.0.0' makes the server accessible from any IP address,
    # not just 'localhost'.
    app.run(debug=True, host='0.0.0.0', port=5001)