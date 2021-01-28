from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def index():
	return "welcome to the course"

bank_statement = [{'id':1,"date":"20-01-2020","transaction":"cheque deposit 123zzxdrgg by ABC","debit":"10000","credit":'',"balance":"55000"},
{'id':2,"date":"15-02-2020","transaction":"EMI paid to XYZ","debit":"5000","credit":'',"balance":"50000"},
{'id':3,"date":"30-03-2020","transaction":"salary credited","debit":"","credit":"35000","balance":"85000"}]

@app.route("/bankdata", methods=['GET'])
def show_data():
	return jsonify({'bank_statements':bank_statement})

@app.route("/add_data",methods=['POST'])
def insert_bankdetails():

	date = request.form["date"]
	trans = request.form["transaction"]
	debit = request.form["debit"]
	credit = request.form["credit"]
	balance = request.form["balance"]
	id = bank_statement[-1]['id']+1
	new_obj = {'id':id, 'date':date, 'transaction':trans, 'debit':debit, 'credit':credit, 'balance':balance }
	#insert_data = {'id':4,"date":"12-04-2020","transaction":"ATM transaction","debit":"1000","credit":'',"balance":"49000"}
	bank_statement.append(new_obj)
	return jsonify({"updated_banktrans": bank_statement}), 201

@app.route("/bankdata/<int:id>", methods=['GET','PUT','DELETE'])
def single_bankdetails(id):
	if request.method == 'GET':
		for item in bank_statement:
			if item['id'] == id:
				return jsonify({'bank_statements':item})
	
		
	elif request.method == 'PUT':
		for item in bank_statement:
			if item['id'] == id:
				date = request.form["date"]
				trans = request.form["transaction"]
				debit = request.form["debit"]
				credit = request.form["credit"]
				balance = request.form["balance"]
				updated_data = {'id':id, 'date':date, 'transaction':trans, 'debit':debit, 'credit':credit, 'balance':balance }
				#{'id':id,"date":"25-12-2020","transaction":"cheque deposit 123zzxdrgg by ABC","debit":"10000","credit":'',"balance":"55000"}
				return jsonify(updated_data)

	elif request.method == 'DELETE':
		for idx,item in enumerate(bank_statement):
			if item['id'] == id:
				bank_statement.pop(idx)
				return jsonify(bank_statement)




if __name__ == "__main__":
	app.run(debug=True)