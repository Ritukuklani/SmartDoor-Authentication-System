
var chatHistory = [];
var apigClient = null;
// const AWS =require('aws-sdk');
var url_string = window.location.href;
function callInputLambda() {
  var itext = document.getElementById('name-text').value.trim()
  // var inputText = itext.toLowerCase();
  document.getElementById('name-text').value = "";
  if(itext == "") {
    alert("Sorry! You entered wrong OTP.");
    return false;
  }
  else {
    // chatHistory.push("User: " + itext);
    // chatHistory.push("User: " + ptext);
    // document.getElementById('chat-output').innerHTML = "";
    // chatHistory.forEach((element) => {
    //   document.getElementById('chat-output').innerHTML += "<p>" + element + "</p>";
     };
     console.log(itext);
  setTimeout(chatbotResponse, 500, itext);
  
  return false;
  
  //return chatbotResponse(inputText,phonenumberText);
}


function chatbotResponse(itext) {
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
      "otp":itext
    };
    var additionalParams = {
      // headers: {
      //   'x-api-key': 'Your API KEY'
      // },
      // queryParams: {}
    };
    console.log(body)
    return apigClient.validateOTPPost(params,body,additionalParams)
  // // })
   .then((result) =>{
    r1 = result["data"];
    console.log(r1);
    // r2 = JSON.stringify(r1);
    // r3 = r2.substring(3, r2.length-3);
    if (r1=='false'){
      chatHistory.push("you can not enter through the virtual door");
    }
    else{
      chatHistory.push(r1 + " you can enter through the virtual door");
    }
   
      document.getElementById('chat-output').innerHTML = "";
      // console.log(result.message)
      chatHistory.forEach((element) => {
        document.getElementById('chat-output').innerHTML += "<p>" + element + "</p>";
      });
  })
  .catch((err) =>{
    console.log(err);
  });
 }


