import boto3
import json

client = boto3.client('lambda')

payload = {"names": ["Student1", "Student2", "Student3"]}
json_string = json.dumps(payload, skipkeys=True)
encoded_payload = json_string.encode('utf-8')

response = client.invoke(
    FunctionName='arn:aws:lambda:us-east-1:765472542773:function:HelloStudentFunction',
    Payload=encoded_payload,
)

res_bytes = response['Payload'].read()
bytes_decoded = res_bytes.decode('utf-8')
res_data = json.loads(bytes_decoded)

print(res_data)
