import boto3
import json
import datetime
import uuid
import base64

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Constants
BUCKET_NAME = 'new-resume123'  # Replace with your bucket
TABLE_NAME = 'applicants'      # Replace with your table

def lambda_handler(event, context):
    try:
        # Handle preflight request for CORS
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'message': 'CORS preflight OK'})
            }

        # Parse form data (multipart/form-data)
        content_type = event['headers'].get('content-type') or event['headers'].get('Content-Type')
        body = base64.b64decode(event['body']) if event.get("isBase64Encoded", False) else event['body'].encode()


        # We'll parse form-data manually
        name, email, file_name, file_bytes = parse_multipart(body, content_type)

        # Generate unique filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{name.replace(' ', '_')}_{timestamp}_{file_name}"

        # Upload to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=unique_filename, Body=file_bytes)

        # Save to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'resume_filename': unique_filename,
            'uploaded_at': timestamp
        })

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'message': f"Thank you {name}, your resume has been uploaded successfully!"})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
        'Access-Control-Allow-Headers': '*'
    }

def parse_multipart(body, content_type):
    import re
    boundary = content_type.split("boundary=")[1]
    parts = body.split(f"--{boundary}".encode())

    name = email = file_name = None
    file_bytes = b""

    for part in parts:
        if b"Content-Disposition" in part:
            header, content = part.split(b"\r\n\r\n", 1)
            content = content.rstrip(b"\r\n")

            disposition = header.decode(errors="ignore")

            if 'name="name"' in disposition:
                name = content.decode()
            elif 'name="email"' in disposition:
                email = content.decode()
            elif 'name="resume"' in disposition:
                match = re.search(r'filename="(.+)"', disposition)
                if match:
                    file_name = match.group(1)
                    file_bytes = content

    return name, email, file_name, file_bytes