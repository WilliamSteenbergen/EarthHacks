from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def my_form():
	return render_template('main.html')

@app.route('/', methods=['POST'])
def my_form_post():
	lat = request.form['Latitude']
	lon = request.form['Longitude']

	return render_template('map.html', post={'latitude': lat, 'longitude': lon})

if __name__ == "__main__":
	app.run(port=0, debug=True)