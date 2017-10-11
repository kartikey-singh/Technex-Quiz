var sl = 25,
sec = 11,
click = 0,
my;
var user_email = document.getElementById("user").innerHTML;
var first = {email:user_email};
var json_parsing;
function ajax_get(first){
  $.ajax({
    url: "test/", // the endpoint
    type: "POST", // http method
    data: first, // data sent with the post request
    // handle a successful response
    success: function(json) {
      json_parsing = json;
      console.log(json); // log the returned json to the console
      console.log("success"); // another sanity check
    },
 
    async: false
    // handle a non-successful response
    
            });
}
ajax_get(first);

console.log(json_parsing.single[0].id);
//var json_p = JSON.parse(json_parsing);
//console.log(json_p)
/*var obj = JSON.parse(
  '{"status":1,"s_time":"f","e_time":"d","u_time":"q","ids":12,"single": [{"id": 1,"question": "this is a question1?","option": ["option1","option2","option3","option4"],"optionID":[1,2,3,4]},{"id": 2,"question": "this is a question2?","option": ["option1","option2","option3","option4"]},{"id": 3,"question": "this is a question3?","option": ["option1","option2","option3","option4"]},{"id": 4,"question": "this is a question4?","option": ["optionu1","optionu2","optionu3","optionu4"]}],"multiple": [{"id": 5,"question": "this is a multiple question1?","option": ["optionm1","option2lj","option3","option4"]},{"id": 6,"question": "this is a multiple question2?","option": ["optionm1","option2j","option3","option4"]},{"id": 7,"question": "this is a multiple question3?","option": ["optionm1","option2gg","option3","option4"]},{"id": 8,"question": "this is a multiple question4?","option": ["optionm1","option2h","option3","option4"]}],"integer": [{"id": 9,"question": "this is a int question1?"},{"id": 10,"question": "this is a int question2?"},{"id": 11,"question": "this is a int question3?"},{"id": 12,"question": "this is a int question4?"}]}'
  );*/

 var t = '{"status":1,"s_time":"f","e_time":"d","u_time":"q","ids":12,"single": [{"id": 1,"question": "this is a question1?","option": ["option1","option2","option3","option4"],"optionID":[1,2,3,4]}],"multiple": [{"id": 5,"question": "this is a multiple question1?","option": ["optionm1","option2lj","option3","option4"],"optionID": [5, 6, 7, 8]}],"integer": [{"id": 9,"question": "this is a int question1?"},{"id": 10,"question": "this is a int question2?"},{"id": 11,"question": "this is a int question3?"},{"id": 12,"question": "this is a int question4?"}]}';

//   console.log(t);
  //var obj = JSON.parse(t);
 //console.log(obj.single);
 console.log(obj);
var obj = json_parsing;








 ///// All correct below
$("#questions,#thanks,#final").hide();
//  For SIDEBAR
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
  if (point === 1) point = 2;
  $("html, body").animate(
  {
    scrollTop: $("#submit" + (point - 1)).offset().top
  },
  300
  );
}

// TIMER implement again
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
  $("#help").hide();
  $("#questions,#final").show();
  menu();
  read();
  my = setInterval(function() {
    myTimer();
  }, 1000);
});
$("#final").click(function() {
  if (click === 0) {
    click++;
    alert("Are you sure that you want to submit the quiz answers !!!");
    $("#final").text("Final Submission");
  } else {
    clearInterval(my);
    $("#questions").hide();
    $("#thanks").show();
  }
});
var submission = [];
for (var i = 0; i < obj.ids; i++) {
  submission.push(0);
}

function hider(sub) {
  $("#error" + sub).hide();
}
function single(check, sub) {
  hider(sub);
  var f = 0;
  if (document.getElementById("test" + (check - 3)).checked) {
    f = 1;
    submission[sub - 1] = 1;
  } else if (document.getElementById("test" + (check - 2)).checked) {
    f = 1;
    submission[sub - 1] = 2;
  } else if (document.getElementById("test" + (check - 1)).checked) {
    f = 1;
    submission[sub - 1] = 3;
  } else if (document.getElementById("test" + check).checked) {
    f = 1;
    submission[sub - 1] = 4;
  } else {
    $("#error" + sub).show();
  }
  if (f === 1) {
    console.log(submission);
    $("#error" + sub)
    .show()
    .text(
      "You have submitted Option " + submission[sub - 1] + " as your answer."
      );
  }
  var test = {user_email:user_email ,type:"single",question_id: sub,option:submission[sub-1],mul_option:"NULL"};
  ajax_post(test);
}

function multiple(check, sub) {
  var v = [];
  if (document.getElementById("test" + (check - 3)).checked) v.push(1);
  if (document.getElementById("test" + (check - 2)).checked) v.push(2);
  if (document.getElementById("test" + (check - 1)).checked) v.push(3);
  if (document.getElementById("test" + check).checked) v.push(4);
  if (v.length === 0) $("#error" + err).show();
  else {
    var s = "";
    for (var i = 0; i < v.length; i++) {
      s += v[i] + " , ";
    }
    $("#error" + sub)
    .show()
    .text("You have submitted Option " + s + " as your answer.");
    submission[sub - 1] = v;
    console.log(submission);
    var s = ""  + submission[sub-1] + "";
    var test = {user_email:user_email ,type:"multiple",question_id: sub,mul_option:s,option:0};
    ajax_post(test);
  }
}
function numerical(na, sub) {
  var input = document.getElementById("num" + na).value;
  var a = parseInt(input);
  if (a >= 0 && a <= 9) {
    submission[sub - 1] = a;
    $("#error" + sub)
    .show()
    .text("You have submitted " + submission[sub - 1] + " as your answer.");
    console.log(submission);
    var test = {user_email:user_email ,type:"numerical",question_id: sub,option:submission[sub-1],mul_option:"NULL"};
    ajax_post(test);
  } else
  $("#error" + sub).show().text("Please enter a numeric value between 0-9");
}

function ajax_post(test){
  $.ajax({
    url: "create_post/", // the endpoint
    type: "POST", // http method
    data: test, // data sent with the post request
    // handle a successful response
    success: function(json) {
      console.log(json); // log the returned json to the console
      console.log("success"); // another sanity check
    },
    // handle a non-successful response
    error:  function(xhr,errmsg,err) {
      $('#error1').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
              }
            });
}
function reset(val, check, type) {
  submission[val - 1] = 0;
  hider(val);
  if(type === 1 || type === 2){
    document.getElementById("test" + (check - 3)).checked = false;
    document.getElementById("test" + (check - 2)).checked = false;
    document.getElementById("test" + (check - 1)).checked = false;
    document.getElementById("test" + check).checked = false;
    var test = (type === 1) ? {user_email:user_email ,type:"single",question_id: val,option:0,mul_option:"NULL"} :
               {user_email:user_email ,type:"multiple",question_id: val,option:0,mul_option:"NULL"} ;
    ajax_post(test);
  }
  else{
    document.getElementById("num" + (check)).value = "";
    var test = {user_email:user_email ,type:"numerical",question_id: val,option:0,mul_option:"NULL"};  
    ajax_post(test);
  }
}

function read() {
  var sin = obj.single;
  var mul = obj.multiple;
  var num = obj.integer;
  var na = 1; //for numerical questions
  var x = 4; //for tests and creating new ID's
  var sub = 1; //for submission
  var start =  "<div class='row' id='card" +
    sub +
    "'><div class='col s12 m12'><div class='card teal accent-1 hoverable'><div class='card-content  center-align'><span class='card-title'>" +
    "Question " ;

  sin.forEach(function(single) {
    var test =
    start + 
    single.id + 
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
    x +
    "," +
    sub +
    ")' id='submit" +
    sub +
    "'>Submit</button><button class='btn' onclick='reset(" +
    sub +
    "," +
    x +
    ",1)' id='reset" +
    sub +
    "'>Reset</button></div></div></div></div>";  
    $("#questions").append(test);
    // console.log(test);
    x += 4; // for implementing new id for options (if 4 options question)
    sub++;
  });
  mul.forEach(function(multiple) {
    var test =
    start + multiple.id +
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
    x +
    "," +
    sub +
     ")' id='submit" +
    sub +
    "'>Submit</button><button class='btn' onclick='reset(" +
    sub +
    "," +
    x +
    ",2)' id='reset" +
    sub +
    "'>Reset</button></div></div></div></div>";
    $("#questions").append(test);
    //console.log(test);
    x += 4;
    sub++;
  });
  num.forEach(function(number) {
    var test =
    start +
    number.id +
    "</span><form action='#'><p>" +
    number.question +
    "</p><div class='row'><div class='input-field col s6'>" +
    "<input placeholder='Only 0-9 are possible answers' id='num" +
    na +
    "' type='text' class='validate'>" +
    "<label for='num" +
    na +
    "'></label></div></div></form><h6 hidden id='error" +
    sub +
    "'>Please enter a numeric value between 0 to 9</h6></div><div class='card-action center'><button class='btn' onclick='numerical(" +
    na +
    "," +
    sub +
     ")' id='submit" +
    sub +
    "'>Submit</button><button class='btn' onclick='reset(" +
    sub +
    "," +
    na  +
    ",3)' id='reset" +
    sub +
    "'>Reset</button></div></div></div></div>";
    $("#questions").append(test);
    //console.log(test);
    na++;
    sub++;
  });
}
