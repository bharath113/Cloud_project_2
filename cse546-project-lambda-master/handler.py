import os

from boto3 import client as boto3_client
from boto3.dynamodb.conditions import Key
import boto3
import face_recognition
import pickle
import csv

from boto3.dynamodb.conditions import Key

input_bucket = "cse546proj2bharathshrutikaveri"
output_bucket = "cse546proj2outputbharathshrutikaveri"
# util_bucket = "cse546proj2utilbharathshrutikaveri"

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):
	s3 = boto3_client('s3')
	dynamodb = boto3.resource('dynamodb')
	print("Lambda event is triggered.")
	key = event['Records'][0]['s3']['object']['key']
	print(f"Input bucket: {input_bucket}, key:{key}")

	with open('/tmp/'+key, 'wb') as f:
		s3.download_fileobj(input_bucket, key, f)
	name, extension = key.split('.')
	print(f"Name: {name}, extension: {extension}")

	# with open('/tmp/encoding', 'wb') as f:
	# 	s3.download_fileobj(util_bucket, 'encoding', f)
	# print(f"key: {key}")

	os.system(f"ffmpeg -i /tmp/{key} -r 1 /tmp/image-%3d.jpg")
	
	files = os.listdir("/tmp/")
	print(f"files: {files}")
	
	unknown_image = face_recognition.load_image_file(f"/tmp/image-001.jpg")
	unknown = face_recognition.face_encodings(unknown_image)[0]

	encoding = open_encoding('encoding')
	names = encoding['name']
	known = encoding['encoding']

	results = face_recognition.compare_faces(known, unknown)
	i = 0
	while i < len(results):
		if results[i]:
			break
		i += 1

	print(f"Encoding names: {names}, index: {i}")
	print(f"Results: {results}")

	table = dynamodb.Table('StudentData')
	response = table.query(KeyConditionExpression=Key('name').eq(names[i]))

	item = response['Items'][0]
	print(f"Item response: {item}")
	header = ["Name", "Major", "Year"]
	data = [item['name'], item['major'], item['year']]
	with open(f'/tmp/{name}.csv', 'w', encoding='UTF8', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(header)
		writer.writerow(data)
	s3.upload_file(f"/tmp/{name}.csv", output_bucket, f"{name}.csv")
	# with open(f'/tmp/{name}1.csv') as f:
	# 	f.write(f"{item['name'], item['major'], item['year']}")
	# s3.upload_file(f"/tmp/{name}1.csv", output_bucket, f"{name}1.csv")
	# s3.upload_file(output_bucket, key, f)

