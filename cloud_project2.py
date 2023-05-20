import json
import yaml
import boto3


with open('config/config.yaml') as fh:
    config_data = yaml.load(fh, Loader=yaml.FullLoader)


def create_buckets():
    s3 = boto3.client('s3')
    print("\ncreating buckets")
    response = s3.create_bucket(Bucket=config_data['s3-input'])
    print(response)
    response = s3.create_bucket(Bucket=config_data['s3-output'])
    print(response)
    # response = s3.create_bucket(Bucket=config_data['util'])
    # print(response)
    # with open('cse546-project-lambda-master/encoding', 'rb') as f:
    #     s3.upload_fileobj(f, config_data['util'], "encoding")
    print("Buckets created")


def delete_bucket(s3, response, bucket):
    try:
        s3_resource = boto3.resource('s3').Bucket(bucket)
        print(f"deleting bucket: {bucket}")
        s3_resource.objects.all().delete()
        s3_resource.delete()
    except:
        print(f"Error Deleting {bucket}")


def delete_buckets():
    s3 = boto3.client('s3')
    print("\nChecking for existing buckets")
    response = s3.list_buckets()
    if config_data['s3-input'] in response:
        delete_bucket(config_data['s3-input'])
    if config_data['s3-output'] in response:
        delete_bucket(config_data['s3-output'])
    # if config_data and config_data['util'] in response:
    #     delete_bucket(config_data['util'])

    print(f"Deleted buckets.")


def create_db():
    print("creating dynamodb")
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName='StudentData',
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'id',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    table.wait_until_exists()
    print("DynamoDB crated")
    return table


def load_db(table):
    print("Loading data")
    students = []

    with open('cse546-project-lambda-master/student_data.json', 'r') as f:
        # for row in f:
        #     students.append(json.loads(row))
        students = json.load(f)

    with table.batch_writer() as batch:
        for item in students:
            batch.put_item(Item=item)
    print("data loaded into dynamodb")

def delete_db(dynamodb=None):
    print("checking for tables")
    dynamodb = boto3.client('dynamodb')
    table_names = dynamodb.list_tables()['TableNames']
    for table in table_names:
        # specify the table to be deleted
        dynamodb.delete_table(TableName=table)
        waiter = dynamodb.get_waiter('table_not_exists')
        waiter.wait(TableName=table)
    print("deleted tables")

def create_lambda():
    print("creating lambda function")
    iam_client = boto3.client('iam')

    # role_policy = {
    #     "Version": "2012-10-17",
    #     "Statement": [
    #         {
    #             "Sid": "",
    #             "Effect": "Allow",
    #             "Principal": {
    #                 "Service": "lambda.amazonaws.com"
    #             },
    #             "Action": "sts:AssumeRole"
    #         }
    #     ]
    # }
    #TODO: ADD ROLES
    # response = iam_client.create_role(
    #     RoleName='LambdaExecution',
    #     AssumeRolePolicyDocument=json.dumps(role_policy),
    # )

    # print(response)

    lambda_client = boto3.client('lambda', region_name=config_data['region'])
    role = iam_client.get_role(RoleName='LambdaExecution')

    response = lambda_client.create_function(
        FunctionName=config_data['lambda-name'],
        # Runtime=config_data['runtime'],
        Role=role['Role']['Arn'],
        # Handler=config_data['lambda_name'],
        PackageType="Image",
        Code=dict(ImageUri=config_data['lambda-uri']),
        Timeout=900,  # Maximum allowable timeout
        MemorySize=1024,
        Architectures=['arm64'],
    )
    waiter = lambda_client.get_waiter('function_active')
    waiter.wait(FunctionName=config_data['lambda-name'])

    print(response)
    print("lambda function is created.")


def create_lambda_trigger():
    print("\nCreating lambda trigger")
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda', region_name=config_data['region'])
    input_bucket_arn = f"arn:aws:s3:::{config_data['s3-input']}"
    # lambda_client.remove_permission(FunctionName=config_data['lambda-name'], StatementId="S3InvokeLambda")
    response = lambda_client.add_permission(FunctionName=config_data['lambda-name'],
                                       StatementId='S3InvokeLambda',
                                       Action='lambda:InvokeFunction',
                                       Principal='s3.amazonaws.com',
                                       SourceArn=input_bucket_arn
                                       )
    print(response)

    response2 = lambda_client.get_policy(FunctionName=config_data['lambda-name'])
    print(response2)
    lambda_client = boto3.client("lambda")
    lambda_function = lambda_client.get_function(FunctionName=config_data["lambda-name"])
    print(lambda_function["Configuration"]["FunctionArn"])

    response = s3.put_bucket_notification_configuration(
        Bucket=config_data['s3-input'],
        NotificationConfiguration={'LambdaFunctionConfigurations': [
            {'LambdaFunctionArn': lambda_function["Configuration"]["FunctionArn"], 'Events': ['s3:ObjectCreated:Put']}]})
    
    print(response)
    print("Lambda trigger created")

def delete_lambda():
    # iam_client = boto3.client('iam')
    # 
    # #response = iam_client.delete_role(RoleName='LambdaExecution')
    # #print(response)
    lambda_client = boto3.client('lambda')
    function_names = lambda_client.list_functions()["Functions"]
    for function in function_names:
        response = lambda_client.delete_function(
            FunctionName=function["FunctionName"]
        )
        print(response)


if __name__ == "__main__":

    # Clear Env
    delete_buckets()
    delete_lambda()
    delete_db()

    # Setup Env
    load_db(create_db())
    create_lambda()
    create_buckets()
    create_lambda_trigger()

'''
Test 1: Create table, upload student data, query student data
Test 2: Create lambda, run a video, retrieve student data from dynamodb
Test 3: Upload image, call trigger, run the whole thing, output to s3 bucket
Test 4: Create all resources, delete all resources
'''


