import sys
sys.path.insert(0, '/var/www/flaskdemo')
from flaskdemo import app as application

if __name__ == "__main__":
    application.run()
