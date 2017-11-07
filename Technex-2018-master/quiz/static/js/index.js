var sl=0,sec=0,click=0,my,user_email = document.getElementById("user").innerHTML,first = {email:user_email},obj;
function ajax_get(first){
  $.ajax({
    url: "starttest/",        // the endpoint
    type: "POST",             // http method
    data: first,              // data sent with the post request
    success: function(json) { // handle a successful response
      obj = json;
      console.log(obj);       // log the returned json to the console
    },
    async: false
  });
}

ajax_get(first);

function timecalc(){
  var bool = true;
  var duration = obj.duration;
  var sDate = new Date(obj.s_time);
  var eDate = new Date(obj.e_time);
  var uDate = new Date(obj.u_time);
  var timeLeft =  ((eDate-uDate)/1000); // in Seconds
  if(timeLeft < 0){
    timeLeft = 0;
    bool = false;
  }
  else if( (duration*60) < timeLeft ){
     timeLeft = duration*60;
  }
  var minutesLeft = Math.trunc(timeLeft / 60, 0);
  var secondsLeft = timeLeft % 60;
  sl = parseInt(minutesLeft);
  sec = parseInt(secondsLeft);
  return bool;
}

$("#questions,#thanks,#final").hide();

$(".modal-trigger").leanModal();

function openNav() {
  document.getElementById("mySidenav").style.width = "150px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
}

function menu() {
  var all = obj.ids;
  for (var ida = 1; ida <= all; ida++) {
    $(".sidenav").append(
      "<a id='card" +
      ida +
      "' onclick = scrol(" +
      ida +
      ")>Question " +
      ida +
      "</a>"
      );
  }
}
function scrol(point) {
  $("html, body").animate(
  {
    scrollTop: $("#submit" + (point - 1)).offset().top
  },
  300
  );
}

function myTimer() {
  if (sec === 59 && sl !== 0){
    sl--;
    $("#yo").text(sl + "m : " + sec + "s");
    sec--;
  } else if (sec === 0 && sl !== 0) {
    if (sl === 1) {
      Materialize.toast("Only 5 minutes remaining !!", 4000);
    }
    sl--;
    sec = 59;
    $("#yo").text(sl + "m : " + sec + "s");
  } else if (sec === 0 && sl === 0) {
    $("#questions").hide();
    $("#thanks").show();
    clearInterval(my);
  } else {
    sec--;
    if (sec >= 0 && sec <= 9) $("#yo").text(sl + "m : 0" + sec + "s");
    else $("#yo").text(sl + "m : " + sec + "s");
  }
}

$("#start").click(function() {
  var bool = timecalc();
  if(obj.status === 1 && bool === true){
    $("#help").hide();
    $("#questions,#final").show();
    my = setInterval(function() {
      myTimer();
    }, 1000);
    menu();
    read();
  }
  else{
    $("#help").hide();
    $("#errorText").text("Oops! No quiz found for you ");
    $("#thanks").show();
    console.log("error");
  } 
});

$("#final").click(function() {
  if (click === 0) {
    click++;
    alert("Are you sure that you want to submit the quiz answers !!!");
    $("#final").text("Final Submission");
  } else {
    $(".sidenav").html("<a href='javascript:void(0)' class='closebtn' onclick='closeNav()'>&times;</a><a>Thank You</a>");
    clearInterval(my);
    $("#questions").hide();
    $("#thanks").show();
  }
});

function hider(sub) {
  $("#error" + sub).hide();
}

function single(check, sub, id, options) {
  hider(sub);
  var f = 0,option = "";
  if (document.getElementById("test" + (check - 3)).checked) {
    f = 1;
    option = options[0].toString();
  } else if (document.getElementById("test" + (check - 2)).checked) {
    f = 2;
    option = options[1].toString();
  } else if (document.getElementById("test" + (check - 1)).checked) {
    f = 3;
    option = options[2].toString();
  } else if (document.getElementById("test" + check).checked) {
    f = 4;
    option = options[3].toString();
  } else {
    $("#error" + sub).show();
  }
  if (f !== 0) {
    $("#error" + sub).show().text("You have submitted Option " + f + " as your answer.");
  }
  var test = {email:user_email,questionId: id,optionIds:option};
  console.log(test);
  ajax_post(test,"submitques/");
}

function multiple(check, sub, id, options) {
  var v = [], option = [];
  if (document.getElementById("test" + (check - 3)).checked) {
    v.push(1);
    option.push(options[0]);}
  if (document.getElementById("test" + (check - 2)).checked) {
    v.push(2);
    option.push(options[1]);}
  if (document.getElementById("test" + (check - 1)).checked) {
    v.push(3);
    option.push(options[2]);}
  if (document.getElementById("test" + check).checked) {
    v.push(4);
    option.push(options[3]);}
  if (v.length === 0) $("#error" + sub).show();
  else {
    var option = option.join(',');
    var s = v.join(',');
    $("#error" + sub).show().text("You have submitted Option " + s + " as your answer.");
    var test = {email: user_email,questionId: id,optionIds: option};
    console.log(test);
    ajax_post(test,"submitques/");
  }
}

function ajax_post(test,URL){
  $.ajax({
    url: URL,           // the endpoint
    type: "POST",       // http method
    data: test,         // data sent with the post request
    success: function(json) {
      console.log(json);     
    },
    error:  function(xhr,errmsg,err) {
      $('#error1').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+ 
        " <a href='#' class='close'>&times;</a></div>");     // add the error to the dom
        console.log(xhr.status + ": " + xhr.responseText);   // provide a bit more info about the error to the console
        }
      });
}

function reset(val, check, id, type) {
  hider(val);
  if(type === 1){
    document.getElementById("test" + (check - 3)).checked = false;
    document.getElementById("test" + (check - 2)).checked = false;
    document.getElementById("test" + (check - 1)).checked = false;
    document.getElementById("test" + check).checked = false;
    var test = {email:user_email,questionId: id};
    console.log(test);
    ajax_post(test,"resetques/");
    $("#error" + val).text("Please select an option");
  }
  else{
    var test = {email:user_email ,questionId: id};  
    ajax_post(test,"resetques/");
  }
}

function read() {
  var sin = obj.single;
  var mul = obj.multiple;
  var num = obj.integer;
  var na = 1;    //for numerical questions
  var x = 4;     //for tests and creating new ID's
  var sub = 1;   //for submission
  var start =  "<div class='row' id='card" +
    sub +
    "'><div class='col s12 m12'><div class='card teal accent-1 hoverable'><div class='card-content  center-align'><span class='card-title'>" +
    "Question " ;
  var pre = "<div id='submit0'>"+
  "</div>";
  $("#questions").append(pre);
  sin.forEach(function(single) {
    var test = 
    start + 
    sub + 
    "</span><form action='#'><p>" +  
    single.question + 
    "</p><p><input name='group1' type='radio' id='test" +
    (x - 3) +
    "'/><label for='test" +
    (x - 3) +
    "'>" +
    single.option[0] +
    "</label></p><p><input name='group1' type='radio' id='test" +
    (x - 2) +
    "'/><label for='test" +
    (x - 2) +
    "'>" +
    single.option[1] +
    "</label></p><p><input name='group1' type='radio' id='test" +
    (x - 1) +
    "'/><label for='test" +
    (x - 1) +
    "'>" +
    single.option[2] +
    "</label></p><p><input name='group1' type='radio' id='test" +
    x +
    "'/><label for='test" +
    x +
    "'>" +
    single.option[3] +
    "</label></p></form>" +
     "<h6 hidden id='error" +
    sub +
    "'>Please select an option</h6></div><div class='card-action center'><button class='btn'  onclick='single(" +
    x   +
    "," +
    sub +
    "," +
    single.id +
    ",[" +
    single.optionID +
     "])' id='submit" +
    sub +
    "'>Submit</button><button class='btn' onclick='reset(" +
    sub +
    "," +
    x   +
    "," +
    single.id +
    ",1)' id='reset" +
    sub +
    "'>Reset</button></div></div></div></div>";  
    $("#questions").append(test);
    //console.log(test);
    x += 4; // for implementing new id for options (if 4 options question)
    sub++;
  });
  mul.forEach(function(multiple) {
    var test =
    start + sub +
    "</span><form action='#'><p>" +
    multiple.question +
    "</p><p><input type='checkbox' id='test" +
    (x - 3) +
    "' />" +
    "<label for='test" +
    (x - 3) +
    "'>" +
    multiple.option[0] +
    "</label></p><p><input type='checkbox' id='test" +
    (x - 2) +
    "' /><label for='test" +
    (x - 2) +
    "'>" +
    multiple.option[1] +
    "</label></p><p><input type='checkbox' id='test" +
    (x - 1) +
    "' /><label for='test" +
    (x - 1) +
    "'>" +
    multiple.option[2] +
    "</label></p><p><input type='checkbox' id='test" +
    x +
    "' /><label for='test" +
    x +
    "'>" +
    multiple.option[3] +
    "</label></p></form><h6 hidden id='error" +
    sub +
    "'>Please select atleast one option</h6>" +
    "</div><div class='card-action center'><button class='btn' onclick='multiple(" +
    x   +
    "," +
    sub +
    "," +
    multiple.id +
    ",[" +
    multiple.optionID +
     "])' id='submit" +
    sub +
    "'>Submit</button><button class='btn' onclick='reset(" +
    sub +
    "," +
    x   +
    "," +
    multiple.id +
    ",1)' id='reset" +
    sub +
    "'>Reset</button></div></div></div></div>";
    $("#questions").append(test);
   //console.log(test);
    x += 4;
    sub++;
  });
}
