# Serverless Webhook Forwarder ➡️
A serverless Amazon Web Services (AWS) based webhook forwarder.

<br/>

## Services Required

1. AWS SQS
2. AWS API Gateway
3. AWS Lambda

<br/>

## Steps
[A. Setup AWS SQS](#a-setup-aws-sqs)  
[B. Setup IAM Policy and Role](#b-setup-iam-policy-and-role)  
⠀⠀[i. IAM Policy](#i-iam-policy)  
⠀⠀[ii. IAM Role](#ii-iam-role)  
⠀⠀[iii. IAM Role (for Lambda)](#iii-iam-role-for-lambda)  
[C. Setup AWS API Gateway](#c-setup-aws-api-gateway)  
[D. Setup Lambda](#d-setup-lambda)  
[E. Steps to get AWS endpoint for webhook](#e-steps-to-get-aws-endpoint-for-webhook)

<br/>
<br/>
<br/>

> You can click on any of the below images to see them in full resolution for details.

<br/>

## A. Setup AWS SQS
Simple Queue Service (SQS) will be used as a buffer for webhook calls. So if the endpoint fails or gives any error, it will store all the webhook calls which are being made from origin.

1. Create SQS queue by opening SQS panel
![](https://i.vgy.me/XPSAIb.png)

2. Create a FIFO queue
![](https://i.vgy.me/aAzU42.png)

3. Enable "**Content-based deduplication**" and set "**Message retention period**" as per your need (14 days recommended)

4. Select "**Basic**" access policy and leave all the other options as it is until you know what are those. 

5. Click on **Create Queue**

6. Copy the **Queue URL** & **ARN** and note it down somewhere.
![](https://i.vgy.me/VMgCc7.png)

<br/>
<br/>
<br/>

## B. Setup IAM Policy and Role
We need permission for AWS services to connect between each other. So in the below steps we'll setup IAM Role and Policy to send Message from API Gateway to SQS and to connect to Lambda

<br/>
<br/>
<br/>

#### i. IAM Policy

1. Search for IAM in AWS and open IAM Panel

2. Go to Policies and Create Policy 

3. Open JSON policy editor and paste the below code  
```json
 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Sid": "VisualEditor0",
             "Effect": "Allow",
             "Action": "sqs:SendMessage",
             "Resource": "{{your-resource-arn}}"
         }
     ]
 }
```
*Replace **{{your-resource-arn}}** with the ARN you copied on Point A.6*
![](https://i.vgy.me/ybjr9y.png)


⠀4.⠀Click on **Next:Tag -> Next:Review**

⠀5.⠀**Name the policy** (something like "api-gateway-to-sqs-policy") and click on **Create Policy**

<br/>
<br/>
<br/>

#### ii. IAM Role
1. Click on **Roles** on left pane and **Create Role**
![](https://i.vgy.me/HnmPMz.png)

2. Select **API Gateway** as service and click on **Next:Permissions -> Next:Tags -> Next:Review**
![](https://i.vgy.me/lrGtKj.png)

3. Name the Role (something like "api-gateway-to-sqs-role") and click on **Create Role**

4. Now open the Role you just created by clicking on it from the list

5. Click on **Attach Policy**
![](https://i.vgy.me/SZhctT.png)

6. Attach the Policy you created above (in this example we used "api-gateway-to-sqs-policy" so search for it and attach)

7. Copy the **ARN** of Role and note it down somewhere

<br/>
<br/>
<br/>

#### iii. IAM Role (for Lambda)

1. Create a new **IAM Role** just like Point B.ii.1

2. Select **Lambda** as service and click on **Next:Permissions**

3. Search for the policy "AWSLambdaSQSQueueExecutionRole" and select it to attach.

4. Click on **Next:Tags --> Next:Review**

5. Name the Role (something like "webhook-lambda-sqs-role") and click on **Create Role**

<br/>
<br/>
<br/>

## C. Setup AWS API Gateway
API gateway will be used to receive your webhook calls as a proxy

1. Create API in AWS API Gateway Panel
![](https://i.vgy.me/eVKgMk.png)

2. Click on Build under **Rest API** in the next screen
![](https://i.vgy.me/Kb63QN.png)

3. Give it a Name and Description and click on **Create API**
![](https://i.vgy.me/LWQvyA.png)

4. On next screen click on "**Create Resource**" under **Actions**
![](https://i.vgy.me/zUskIY.png)

5. Fill in the Resource Name and click on Create Resource
![](https://i.vgy.me/04EJ8C.png)

6. Click on **Create Method**
![](https://i.vgy.me/KVvVMl.png)

7. Select **POST** in this dropdown and click on the **Tick icon**
![](https://i.vgy.me/rHDQmx.png)

8. Create Integration Setup with the details mentioned below  
-- **Integration Type**: AWS Service  
-- **AWS Region**: select the preferred region where you want the API to be deployed (you can select any)  
-- **AWS Service**: Simple Queue Service (SQS)  
-- **AWS Subdomain**: you can leave this blank  
-- **HTTP method**: POST  
-- **Action Type**: Use path override  
-- **Path override**: add the SQS queue path here (not the whole URL). The one you noted down in Point A.6 (Queue URL). This will look something like **4998656233/webhook.fifo**  
-- **Execution role**: add the ARN of Execution role you created for SQS in **Point B.ii.7**  
-- **Content Handling**: Passthrough  
-- **Use Default Timeout**: Ticked  
![](https://i.vgy.me/CB8HRP.png)

9. On the next screen select **Integration Request**
![](https://i.vgy.me/iJooMG.png)

10. Scroll down and expand "**Mapping Templates**" and select **Never** for Request body passthrough

11. Click on "**Add mapping template**" and give it the name "**application/json**" and click on the small tick 
![](https://i.vgy.me/XXqwuy.png)
 
12. Scroll down and add `Action=SendMessage&MessageGroupId='master'&MessageBody=$input.body` as the template body and click on **Save**
![](https://i.vgy.me/wVO8D2.png)

13. Just above Mapping templates, click on **HTTP Headers** to expand it and click on "**Add Header**"

14. For **Name** type `Content-Type` and for **Mapped From** type `'application/x-www-form-urlencoded'` and click on the small tick to add it.
![](https://i.vgy.me/Ps2HS7.png)
⠀
 
**After these steps you can test the API call from the Test option in previous screen. If you get any error then go through the previous steps again as you must have definitely missed something**
![](https://i.vgy.me/MxKg5A.png)
⠀
<br/>
<br/>
<br/>⠀

## D. Setup Lambda
AWS Lambda will be used to process messages and forward them to the actual endpoint. 

1. Open Lambda console and fromthe dashboard click on **Create Function** button
![](https://i.vgy.me/NtdbBI.png)

2. Select "Author from Scratch", name the function, chose **Python 3.8** as Runtime, for Execution Role select the Role you created in **Point B.iii.5** and click on "**Create Function**"
![](https://i.vgy.me/OfX1Vc.png)

3. Once the Lambda function is created, open it and click on "**Add Trigger**" button
![](https://i.vgy.me/UbHaLc.png)

4. Select **SQS** as the  trigger and add it, set Batch Size as **1** and click on **Add** button
![](https://i.vgy.me/26Sl1W.png)

5. Select the **Code**  tab and double click on **lambda_function.py** to edit it and replace the code with the below code

```python
import json
import urllib3

def lambda_handler(event, context):
    http = urllib3.PoolManager()
    for record in event['Records']:
        print("test start")
        payload = record["body"]
        print(str(payload))
        r = http.request('POST', 'https://{{api_url}}',
        body=payload, headers={'Content-Type': 'application/json'})
        if r.status != 200:
            context.fail(json.stringify(r.data))
```
*Make sure you replace **{{api_url}}** in the above code with your actual endpoint URL.*

⠀6. ⠀**Save** the code and **Deploy**

<br/>
<br/>
<br/>⠀

## E. Steps to get AWS endpoint for webhook

1. Open AWS API Gateway Panel and edit the API you just created by clicking on it.

2. Deploy the API from the Actions dropdown
![](https://i.vgy.me/kwN0ea.png)

3. Select "**[New Stage]**" and name the stage "**production**" or whatever you like and click on **Deploy**

4. Open **Stages** from the left pane and **expand** the stage you just created, in our case its "production", expand it all the way down to find **POST**
![](https://i.vgy.me/ark0Gp.png)

5. Click on **POST** to open it and here **Invoke URL** is your endpoint where you need to make webhook calls.
![](https://i.vgy.me/1vwcfc.png)

<br/>

### Voila🎉 We are all setup now. You can try sending a test payload.

<br/>
<br/>
<br/>

## Contributing
We welcome all contributors, from casual to regular ❤

Open an issue or a pull request to suggest changes or additions.

<br/>

## License
This repository is released under the [GNU General Public License v3.0](https://github.com/UnitedOver/easy-envato/blob/master/LICENSE "GNU General Public License v3.0")
