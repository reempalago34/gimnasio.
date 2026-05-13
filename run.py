from app import create_app, db

app = create_app()

if __name__ == '__main__':
    #socketio.run(app, host="0.0.0.0", port=80, debug=True, allow_unsafe_werkzeug=True)
    app.run(debug=False, host='0.0.0.0', port=81)