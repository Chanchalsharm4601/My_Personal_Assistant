from flask import Flask , request, jsonify
import main

app = Flask(__name__)

@app.route('/command',methods = ['POST'])
def handle_command():
    data = request.get_json()
    command = data['command']
    response = main.processCommand(command)
    return jsonify({'response': response})

if __name__ =="__main__":
    app.run(host='0.0.0.0',port = 5000)