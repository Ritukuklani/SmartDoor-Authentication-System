
var chatHistory = [];
var apigClient = null;
// const AWS =require('aws-sdk');
var url_string = window.location.href;
// var cognito_token = url_string.substring(url_string.indexOf("=") + 1,url_string.indexOf("&"));

// AWS.config.region = 'us-east-1';
// AWS.config.credentials = new AWS.CognitoIdentityCredentials({
//   IdentityPoolId: 'Your Identity Pool ID',
// 	Logins: {
// 	   'cognito-idp.us-east-1.amazonaws.com/us-east-1_8MsV07uIJ': cognito_token
// 	}
// });

function callInputLambda() {
  var itext = document.getElementById('name-text').value.trim()
  var inputText = itext.toLowerCase();
  document.getElementById('name-text').value = "";
  var ptext = document.getElementById('phonenumber-text').value.trim()
  var phonenumberText = ptext.toLowerCase();
  document.getElementById('phonenumber-text').value = "";
  if(inputText == "") {
    alert("Please enter the name");
    return false;
  }
  else {
    chatHistory.push("User: " + itext);
    chatHistory.push("User: " + ptext);
  //   document.getElementById('chat-output').innerHTML = "";
  //   chatHistory.forEach((element) => {
  //     document.getElementById('chat-output').innerHTML += "<p>" + element + "</p>";
     };
  setTimeout(chatbotResponse, 500, inputText,phonenumberText);
  
  return false;
  
  //return chatbotResponse(inputText,phonenumberText);
}

function chatbotResponse(inputText,phonenumberText) {
  // return AWS.config.credentials.getPromise()
  // .then(()=>{
  //   console.log('Successfully logged!');
  apigClient = apigClientFactory.newClient({
  //     accessKey: AWS.config.credentials.accessKeyId,
  //     secretKey: AWS.config.credentials.secretAccessKey,
  //     // sessionToken: AWS.config.credentials.sessionToken
     });
    var params = {
      
    };
    var body = {
      "name":inputText,
      "phonenumber":phonenumberText
    };
    var additionalParams = {
      // headers: {
      //   'x-api-key': 'Your API KEY'
      // },
      // queryParams: {}
    };
    console.log(body)
    return apigClient.visitordataPost(params,body,additionalParams)
  // // })
  //  .then((result) =>{
      
  //     chatHistory.push("Bot: " + result.message);
  //     document.getElementById('chat-output').innerHTML = "";
  //     console.log(result.message)
  //     chatHistory.forEach((element) => {
  //       document.getElementById('chat-output').innerHTML += "<p>" + element + "</p>";
  //     });
  // })
  // .catch((err) =>{
  //   console.log(err);
  // });
 }


