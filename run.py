from flask_blog import app 

if __name__ == "__main__":

    ## Internally, 
    # app.run --> werkzeug.serving.run_simple -> 
    # werkzueg.serving.make_server().run_forever() || this is just a  While LOOP
    # Listening to Request !!!! 
    app.run(debug=True)