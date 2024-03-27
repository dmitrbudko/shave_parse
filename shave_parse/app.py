from web import app
import main

if __name__ == '__main__':
    main.parser()
    app.run(port=5000, host="0.0.0.0", debug=True)
