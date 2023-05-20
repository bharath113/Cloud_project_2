# Cloud_project_2
This project(Part 2) is a part of course work CSE 546: Cloud Computing

Pre-requisites:
Upload docker image to ECR so that when the lambda function is created, it can pull the container image


What it does:
- Input and Output S3 buckets are created
- Dynamodb table is created
- Student info is populated into the table
- lambda function is created
- trigger from s3 to lambda is created

## Team Members
* Bharath Kumar Bandaru - 1219442718
* Kaveri Subramaniam - 1222089687
* Shruti Pattikara Sekaran - 1222257972

## Project Requirements


### Software Requirements
    Python3
    Boto3 - AWS SDK for python
    face_recognition - Requred for getting encoding values of the face.
    ffmpeg - Needed for frames extraction which contain the faces of the person.
    
### AWS CLI
    Install aws-cli from 
    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### AWS Configuration.
    Use command: aws configure
    ACCESS_KEY_ID = <>
    SECRET_ACCESS_KEY_ID = <>
    REGION = us-east-1
    OUTPUT = JSON

    PEM key file for SSH Access: <>
### Procedure:
    First run requirements.txt
    run python3 cloud_project2.py to create cloud infrastructure
    run python3 workload_generator.py file to send the input-videos to the s3 buckets.
    

