import json
import boto3

dynamo_resource = boto3.resource('dynamodb')
dynamo_visitors_table = dynamo_resource.Table("visitors")
dynamo_passcodes_table = dynamo_resource.Table("passcodes")

def lambda_handler(event, context):
    # TODO implement
    print(event['otp'])
    visitors_provided_otp = event['otp']
    # visitors_provided_otp = "1224"
    passcodes_response = dynamo_passcodes_table.scan()
    otps = []
    
    otp_faceid_dict = {}
    
    for i in range(len(passcodes_response['Items'])):
        
        otp_faceid_dict[passcodes_response['Items'][i]['otp']] = passcodes_response['Items'][i]['faceId']
        print(passcodes_response)
        # print( otp_faceid_dict[passcodes_response['Items'][i]['otp']])
        # print(passcodes_response['Items'][i]['faceId'])
    print(otp_faceid_dict.keys())
    
    # if "3839" in otp_faceid_dict.keys():
    #     print("Heyy")

    if visitors_provided_otp in otp_faceid_dict.keys():
        print("Give access to visitor")       
        key = {'faceId' : otp_faceid_dict[visitors_provided_otp]}   
        visitors_response = dynamo_visitors_table.get_item(Key=key)
        visitors_name = visitors_response['Item']['name']
        visitors_phone = visitors_response['Item']['phoneNumber']
        
        return visitors_name
    else:  
        return "false"
    
    
    print(otp_faceid_dict)
    
    # print(event)
    # otp = event['otp']
    # print(otp)
    # #otp = 3839
    # dynamodb_getotp = boto3.resource('dynamodb').Table("passcodes")
    
    # # key = {'otp' : otp} 
    # # print("key:", key)
    # # get_otp = dynamodb_getotp.get_item(Key=key)
    
    # get_otp = dynamodb_getotp.get_item(
    #                     TableName='passcodes',
    #                     Key={
    #                         'otp': str(otp)
    #                         }
    #                 )
    # print(get_otp)
    # # ans=get_otp['Item']['otp']
    
    # if(get_otp is not None):
    #     print("Retrived OTP successfully from DynamoDB Passcodes mathcing the OTP visitor entered")
    #     print(get_otp['Item']['otp'])
    # else:
    #     print("User entered wrong OTP")
    
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
