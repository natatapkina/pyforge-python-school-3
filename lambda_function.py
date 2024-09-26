import json

def lambda_handler(event, context):
    names: list[str] = event.get('names', ['World'])
    
    body = ''
    
    for name in names:
        body += f'Hello, {name}! '

    return {
        'statusCode': 200,
        'body': body.strip(),
    }
