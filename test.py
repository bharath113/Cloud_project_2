import boto3
import json
import pandas as pd
def check():
    s3 = boto3.resource('s3')
    output_bucket = "cse546proj2outputbharathshrutikaveri"
    bucket = s3.Bucket(output_bucket)
    lines = open("cse546-project-lambda-master/mapping", "r").readlines()
    mappings = {}
    for line in lines:
        line = line.replace("\n", "")
        values = line.replace(",", ":")
        values = values.split(":")
        mappings[values[0].split(".")[0]] = [values[1], values[2]]
    results = {}
    for obj in bucket.objects.all():
        key = obj.key
        body = pd.read_csv(obj.get()['Body'])
        # body = body.decode('utf-8')
        # print(f"Key: {key}, Body: {body['Major'][0]}, {body['Year'][0]}")
        results[key.split(".")[0]] = [body['Major'][0], body['Year'][0]]
    # print(results)
    # print(mappings)

    for key in results.keys():
        original = mappings[key]
        result = results[key]
        val = True
        if original[0] != result[0] or original[1] != result[1]:
            val = False
        print(f"key: {key}, original: {original}, result: {result}, val: {val}")



if __name__ == "__main__":
    check()