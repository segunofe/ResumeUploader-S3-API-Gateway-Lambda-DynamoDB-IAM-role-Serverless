# Resume Uploader (S3 + API Gateway + Lambda + DynamoDB)

This project is a simple serverless application for uploading resumes via a web form.
It uses:

S3 — to host the frontend and store uploaded resumes.
<img width="1920" height="1032" alt="image" src="https://github.com/user-attachments/assets/c9633434-3cfb-4847-9208-485907cdbe67" />

<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/c649a52d-7526-44a2-beea-27d4732f27a7" />


DynamoDB — to store applicant details.

<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/6924385b-e652-43f6-ab09-7164f52e534a" />


Lambda — to process file uploads.

<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/cf4f176e-f06e-4d8a-9000-f2e041457896" />


API Gateway — to expose the Lambda function as an API.


<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/c03f0bd6-c56d-4465-ab30-02e3dd588aad" />

CORS — to allow cross-origin requests from the frontend.

## Architecture Overview

Frontend (index.html) hosted on S3 static website hosting.

API Gateway REST API with /upload resource, linked to a Lambda function.

Lambda function uploads files to S3 and stores metadata in DynamoDB.

DynamoDB table named applicants stores applicant name, email, filename, and timestamp.

CORS enabled at both the stage (prod) and /upload resource level.

Setup Instructions
1. Create an S3 Bucket for the Frontend
Go to S3 Console → Create bucket:

Bucket name: new-resume123 (replace with your own, must be globally unique).

Region: us-east-1 (or your preferred).

Disable Block Public Access.

Enable Static Website Hosting:

Properties → Static website hosting → Enable.

Index document: index.html.

Upload index.html to the bucket.

Add Bucket Policy to make files public:

json
Copy
Edit
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::new-resume123/*"
    }
  ]
}
Save and note the S3 website URL.

2. Create the DynamoDB Table
Go to DynamoDB Console → Create table.

Table name: applicants.

Partition key: id (String).

Leave other settings as default, click Create table.

3. Create the Lambda Function
Go to Lambda Console → Create function:

Name: resumeUploader.

Runtime: Python 3.12 (or latest).

Execution role: Create new role with S3 full access and DynamoDB full access.

Paste your Python code (app.py) into the Lambda function.

Set Environment Variables if needed.

Click Deploy.

4. Create an API Gateway REST API
Go to API Gateway Console → Create API → REST API.

Name it ResumeUploaderAPI.

Create Resource:

Resource name: upload.

Resource path: /upload.

Create POST Method on /upload:

Integration type: Lambda Function.

Select your Lambda (resumeUploader).

Create OPTIONS Method (for CORS preflight):

Mock integration.

In Method Response → Add Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers.

Enable CORS for /upload:

Select /upload → Actions → Enable CORS.

Enable CORS for the prod stage:

After deploying (next step), go to Stage settings and enable CORS.

5. Deploy the API
Go to Actions → Deploy API.

Stage name: prod.

Copy the Invoke URL:

arduino
Copy
Edit
https://<api-id>.execute-api.us-east-1.amazonaws.com/prod
Your /upload endpoint will be:

arduino
Copy
Edit
https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/upload
6. Update index.html
In your JavaScript fetch call, replace the URL with your API Gateway /upload endpoint:

javascript
Copy
Edit
const res = await fetch(
  "https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/upload",
  {
    method: "POST",
    body: formData,
  }
);
7. Test the Application
Open the S3 website URL in your browser.

Fill in name, email, and upload a file.

Check:

File uploaded to S3 in new-resume123 bucket.

Metadata stored in applicants DynamoDB table.

Success message returned in browser.

8. Security Notes
Never expose AWS credentials in the frontend.

Use IAM roles for Lambda instead of hardcoding keys.

You can add file type & size restrictions in the Lambda code.

