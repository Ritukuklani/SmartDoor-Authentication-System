import cv2
import logging
import base64
import json
import boto3
import os
import random as r
import time
from decimal import Decimal
from datetime import datetime



dynamo_resource = boto3.resource('dynamodb')

dynamo_visitors_table = dynamo_resource.Table("visitors")
dynamo_passcodes_table = dynamo_resource.Table("passcodes")

def lambda_handler(event, context):
    # TODO implement
    
    logging.info("API CALLED. EVENT IS:{}".format(event))
    
    print("Data streaming")
    print(event)
    data = event['Records'][0]['kinesis']['data']
    print(base64.b64decode(data))
    json_data = json.loads(base64.b64decode(data).decode('utf-8'))
    stream_name="KVS1"
    print('JSON DATA',json_data)
    
    
    
    smsClient = boto3.client('sns')
    mobile = "+13472486501"
    ownerWebpageLink = "https://ownerauth.s3.amazonaws.com/index.html"
    authorization_link="http://otpauthorization.s3-website-us-east-1.amazonaws.com"
    faceId='123'
    matched_face=None
    face_search_response = json_data['FaceSearchResponse']
    print(len(face_search_response))
    if len(face_search_response)==0:
        return ("No one at the door")
    else:
        matched_face = json_data['FaceSearchResponse'][0]['MatchedFaces']
    
    if face_search_response is not None and ( matched_face is None or len(matched_face)==0):
        timestamp=json_data['InputInformation']['KinesisVideo']['ServerTimestamp']
        print("timestamp")
        print(timestamp)
        fragmentNumber= json_data['InputInformation']['KinesisVideo']['FragmentNumber']
        print("fragmentNumber")
        print(fragmentNumber)
        visitorImageLink,faceId =store_image(stream_name,fragmentNumber, timestamp, None)
        ownerRequestAccessSMS(mobile, visitorImageLink, ownerWebpageLink, faceId)
    else:
        image_id = json_data['FaceSearchResponse'][0]['MatchedFaces'][0]['Face']['ImageId']
        print('IMAGEID',image_id)
        faceId = json_data['FaceSearchResponse'][0]['MatchedFaces'][0]['Face']['FaceId']
        print('FACEID',faceId)

        key = {'faceId' : faceId}   
        visitors_response = dynamo_visitors_table.get_item(Key=key)
        print("Retrived FaceId successfully from DynamoDB mathcing the FaceId with JSON_Data")
        
        keys_list = list(visitors_response.keys())
        
        otp=""
        for i in range(4):
            otp+=str(r.randint(1,9))
        
        if('Item' in keys_list):
            
            print("We are inside the Item")
            phone_number_visitor = visitors_response['Item']['phoneNumber']
            face_id_visitor = visitors_response['Item']['faceId']
            visitors_name = visitors_response['Item']['name']
            visitors_photo = visitors_response['Item']['photos']
            photo={'objectKey':'updatedKey' , 'bucket' : 'bucketforvisitors', 'createdTimestamp' : str(time.ctime(time.time()))}
            visitors_photo.append(photo)
            
            my_visitor_entry = {'faceId' : face_id_visitor , 'name' : visitors_name , 'phoneNumber' : phone_number_visitor , 'photos' : visitors_photo}
            dynamo_visitors_table.put_item(Item=my_visitor_entry)
            
            my_string = {'faceId' : face_id_visitor, 'otp': otp, 'expiration' : str(int(time.time() + 300))}
            dynamo_passcodes_table.put_item(Item=my_string)
            
            response = dynamo_visitors_table.get_item(
                        TableName='visitors',
                        Key={
                            'faceId': face_id_visitor
                            }
                    )
            print('response')
            print(response)
            print(response['Item']['phoneNumber'])
            
            mobile = response['Item']['phoneNumber']
            msg='Hi, here is your otp. Enter this and you can go through the front door! : ' +otp + ' Please enter the otp here ' + authorization_link
            sns = boto3.client('sns')
            print("msg:", msg)
            response = sns.publish(
            PhoneNumber=mobile,
            Message=msg # this should include link to submit visitor info
            )
    # else:
    #     phone_number_owner = '6466230205'
    #     link_visitor_image = 'https://smart-door-trr.s3.amazonaws.com/' + filename
        
        
    #     ####saqib changes start
    #     link_visitor_details_form = 'https://smart-door-trr.s3.amazonaws.com/WebPage_Vistor_Info.html?filename='+fileName+"&faceid="+faceId
    #     ###saqib changes end
        
    #     print("URLs sent to Owner: ")
    #     # sendMessageToOwner(phone_number_owner, link)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    

def store_image(stream_name, fragmentNumber,timestamp, faceId):
    # kvs_client = boto3.client('kinesis-video-archived-media')
    s3_client = boto3.client('s3')
    rekClient=boto3.client('rekognition')
    
    kvs = boto3.client("kinesisvideo")
    # Grab the endpoint from GetDataEndpoint
    endpoint = kvs.get_data_endpoint(
        APIName="GET_HLS_STREAMING_SESSION_URL",
        StreamName=stream_name
   )['DataEndpoint']

    print(endpoint)
    # # Grab the HLS Stream URL from he endpoint
    kvam = boto3.client("kinesis-video-archived-media",
                        endpoint_url=endpoint)
    
    url = kvam.get_hls_streaming_session_url(
            StreamName=stream_name,
            PlaybackMode="LIVE",
            HLSFragmentSelector={
                # 'FragmentSelectorType': 'SERVER_TIMESTAMP',
                # 'TimestampRange': {
                #     'StartTimestamp': timestamp
                # }
            }
        )['HLSStreamingSessionURL']
        
    cap = cv2.VideoCapture(url)
    final_key = 'frame.jpg'
    s3_client = boto3.client('s3')
    bucket = "bucketforvisitors"
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        print(ret)
        print(frame)

        if frame is not None:
        # Display the resulting frame
            cap.set(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2) - 1)
            cv2.imwrite('/tmp/' + final_key, frame)
            s3_client.upload_file('/tmp/' + final_key, bucket, final_key)
            cap.release()
            print('Image uploaded')
            break
        else:
            print("Frame is None")
            break

        # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
        
    location = boto3.client('s3').get_bucket_location(Bucket=bucket)['LocationConstraint']
    print(location)
    s3ImageLink = "https://%s.s3.amazonaws.com/%s" % (bucket, final_key)
    print("s3ImageLink ====" + s3ImageLink)
    
    collectionId="Visitors-Collection"
    if(faceId is None):
        faceId=index_image(frame, collectionId,fragmentNumber)
        # fileName= faceId+'-'+fragmentNumber+'.jpg'
    print("s3ImageLink")
    print(s3ImageLink)
    print("faceId")
    print(faceId)
    return s3ImageLink, faceId
    
#     endpoint = kvs.get_data_endpoint(
#         APIName="GET_MEDIA_FOR_FRAGMENT_LIST",
#         StreamName=stream_name
#     )['DataEndpoint']
#     print("Kinesis Data endpoint: ",endpoint)
#     kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
    
#     kvs_s = boto3.client('kinesis-video-archived-media', endpoint_url=endpoint, region_name='us-east-1')
#     kvs_stream = kvs_s.get_media_for_fragment_list(
#     StreamName=stream_name,
#     Fragments=[
#         fragmentNumber,
#     ])
#     
#     print("KVS Stream: ",kvs_stream)
    
#     with open('/tmp/kvsstream.mkv', 'wb') as f:
#         streamBody = kvs_stream['Payload'].read(1024*16384) 
#         f.write(streamBody)
#         print(f)
#         kvs = boto3.client("kinesisvideo")
#         # Grab the endpoint from GetDataEndpoint
#         endpoint = kvs.get_data_endpoint(
#             APIName="GET_HLS_STREAMING_SESSION_URL",
#             StreamName=streamName
#         )['DataEndpoint']

#         
        
#         # cap = cv2.VideoCapture('/tmp/kstream.mkv')
#         print("cap:", cap)
#         total=int(count_frames_manual(cap)/2)
#         print(total)
#         cap.set(2,total)
#         print(cap)
#         # cap.GrabFrame(capture)
#         ret, frame = cap.read() 
#         print("ret", ret)
#         print("frame", frame)
#         cv2.imwrite('/tmp/frame.jpg', frame)
#         print("after imwrite")
        
#         if(faceId is None):
#             faceId=index_image(frame, collectionId,fragmentNumber)
#         fileName= faceId+'-'+fragmentNumber+'.jpg'
#         s3_client.upload_file(
#             '/tmp/frame.jpg',
#             'bucketforvisitors', 
#             fileName
#         )
#         cap.release()
#         print('Image uploaded')
#         return fileName, faceId

def index_image(frame, collectionId, fragmentNumber):
    rekClient=boto3.client('rekognition')
    print("Inside index_image")
    retval, buffer = cv2.imencode('.jpg', frame)
    print("retval:", retval)
    print("frame:", frame)
    print("buffer:", buffer)
    response=rekClient.index_faces(CollectionId=collectionId,
    Image={'S3Object': {
                        'Bucket': 'bucketforvisitors', 'Name': 'frame.jpg'}},
    ExternalImageId=fragmentNumber,
    DetectionAttributes=['ALL'])
    
    print('New Response',response)
    faceId=''
    for faceRecord in response['FaceRecords']:
        faceId = faceRecord['Face']['FaceId']
    print("faceID:" , faceId)
    return faceId
    
def ownerRequestAccessSMS(mobile,visitorImageLink, webpageLink, faceId):
    visitorImageLink= visitorImageLink
    print("Inside ownerRequestAccessSMS")
    msg = 'Hi, someone is at your apartment front-door.\n View Picture of visitor : ' +visitorImageLink+ '\nApprove/ Deny Entry : ' + webpageLink+"?faceId="+faceId
    sns = boto3.client('sns')
    print("msg:", msg)
    response = sns.publish(
    PhoneNumber=mobile,
    Message=msg # this should include link to submit visitor info
    )
    print("OwnerRequestAccessResponse: ", response)

# def count_frames_manual(video):
# 	total = 0
# 	while True:
# 		(grabbed, frame) = video.read()
# 		if not grabbed:
# 			break
# 		total += 1
# 	print(total)
# 	return total


