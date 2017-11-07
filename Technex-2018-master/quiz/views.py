from django.shortcuts import render, render_to_response, HttpResponse, redirect
from django.http import Http404,JsonResponse,HttpResponseBadRequest
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views import generic
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
import requests, json, facebook, re
from .models import *
import datetime
from django.utils import timezone

#Status Codes
NOTHING_TO_POST = 0
SUCCESS = 1

USER_NOT_FOUND = 2
NO_ACTIVE_QUIZ = 3

QUIZ_NOT_STARTED = 4
QUIZ_HAS_ENDED = 5

RESPONSE_ALREADY_SUBMITTED = 6
RESPONSE_NOT_FOUND = 7
QUESTION_NOT_ATTEMPTED = 8
INVALID_QUESTION = 9
INVALID_OPTIONS = 10
ERROR_ADDING_DATA = 11
TIMES_UP = 12

#Status Text
status_text = {
    NOTHING_TO_POST : "Nothing to post",
    SUCCESS : "Success",

    USER_NOT_FOUND : "User not found",
    NO_ACTIVE_QUIZ : "No active quiz found",

    QUIZ_NOT_STARTED : "Quiz has not started",
    QUIZ_HAS_ENDED : "Quiz has ended",

    RESPONSE_ALREADY_SUBMITTED : "Quiz Response already submitted by the user",
    RESPONSE_NOT_FOUND : "Quiz Response of the user not found",
    QUESTION_NOT_ATTEMPTED : "Question not attempted",
    INVALID_QUESTION : "Invalid Question ID",
    INVALID_OPTIONS : "Invalid Option ID(s)",
    ERROR_ADDING_DATA : "Error adding data to response",
    TIMES_UP : "Time's Up for the user",
}


@csrf_exempt
def StartTest(request):
    response_data = {}
    data = request.POST
    email = data.get("email")

    try:
        user = User.objects.get(email=email)
        try:
            quiz = Quiz.objects.get(activeStatus = True)
        except:
            response_data["status"] = NO_ACTIVE_QUIZ
            response_data["status_text"] = status_text[NO_ACTIVE_QUIZ]
            return JsonResponse(response_data)
        
        # Checks if the start time lies between the quiz timings
        now = timezone.now()
        quizStartTime = quiz.startTime
        if now < quizStartTime:
            response_data["status"] = QUIZ_NOT_STARTED
            response_data["status_text"] = status_text[QUIZ_NOT_STARTED]
            return JsonResponse(response_data)

        quizEndTime = quiz.endTime
        if now > quizEndTime:
            response_data["status"] = QUIZ_HAS_ENDED
            response_data["status_text"] = status_text[QUIZ_HAS_ENDED]
            return JsonResponse(response_data)

        try:
            quizResponse = QuizResponse.objects.get(user=user, quiz=quiz)

            minutes = quizResponse.quiz.duration
            quizEndTime = quizResponse.quiz.endTime
            timediff = now - quizResponse.timeOfAttempt

            if (not quizResponse.activeStatus) or (timediff.total_seconds() > minutes*60):
                quizResponse.activeStatus = False
                quizResponse.save()
                response_data["status"] = RESPONSE_ALREADY_SUBMITTED
                response_data["status_text"] = status_text[RESPONSE_ALREADY_SUBMITTED]
                return JsonResponse(response_data)
        except:
            quizResponse = QuizResponse(user=user, quiz=quiz, timeOfAttempt=now)

        try:
            # Adding the questions and their options to the response
            response_data = getQuizData(quiz.quizId, email)
            
            if response_data is None:
                response_data["status"] = ERROR_ADDING_DATA
                response_data["status_text"] = status_text[ERROR_ADDING_DATA]


            # About the quiz : Adding quiz information
            response_data["name"] = str(quiz.name)
            response_data["description"] = str(quiz.description)
            
            timeFormat = '%d/%m/%Y %H:%M:%S'
            response_data["duration"] = str(quiz.duration)
            response_data["s_time"] = quiz.startTime.strftime(timeFormat)
            response_data["e_time"] = quiz.endTime.strftime(timeFormat)
            response_data["u_time"] = quizResponse.timeOfAttempt.strftime(timeFormat)
            response_data["curr_time"] = now.strftime(timeFormat)


            quizResponse.save() # Save the quizResponse when everything works fine
            response_data["status"] = SUCCESS
            response_data["status_text"] = status_text[SUCCESS]
        except:
            response_data["status"] = ERROR_ADDING_DATA
            response_data["status_text"] = status_text[ERROR_ADDING_DATA]
    except:
        response_data["status"] = USER_NOT_FOUND
        response_data["status_text"] = status_text[USER_NOT_FOUND]
        return JsonResponse(response_data)
    return JsonResponse(response_data)


@csrf_exempt
def SubmitQuestion(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST
        email = data.get("email")
        questionId = data.get("questionId")
        optionIds = data.get("optionIds")

        #Getting the User
        try:
            user = User.objects.get(email=email)
        except:
            response_data['status'] = USER_NOT_FOUND
            response_data['status_text'] = status_text[USER_NOT_FOUND]
            return JsonResponse(response_data)

        #Getting the Quiz
        try:
            quiz = Quiz.objects.get(activeStatus = True)  
        except:
            response_data['status'] = NO_ACTIVE_QUIZ
            response_data['status_text'] = status_text[NO_ACTIVE_QUIZ]
            return JsonResponse(response_data)

        #Checking if the quizResponse of the user is valid or not
        try:
            quizResponse = QuizResponse.objects.get(user=user, quiz=quiz)
            if not quizResponse.activeStatus:
                response_data["status"] = RESPONSE_ALREADY_SUBMITTED
                response_data['status_text'] = status_text[RESPONSE_ALREADY_SUBMITTED]
                return JsonResponse(response_data)
        except:
            response_data['status'] = RESPONSE_NOT_FOUND
            response_data['status_text'] = status_text[RESPONSE_NOT_FOUND]
            return JsonResponse(response_data)

        #Getting the question and the selected options
        try:
            question = Questions.objects.get(questionId=questionId)
            optionIds = optionIds.split(",")
            options = Options.objects.filter(optionId__in = optionIds)
        except:
            response_data['status'] = INVALID_QUESTION
            response_data['status_text'] = status_text[INVALID_QUESTION]
            return JsonResponse(response_data)
        
        now = timezone.now()
        #Submitting the Response if it is valid (i.e. answered within the timelimit)
        try:
            questionResponse = quizResponse.questionresponse_set.get(question=question, quizResponse=quizResponse)
        except:
            questionResponse = QuestionResponse(question=question,quizResponse=quizResponse)
        
        questionResponse.responseTime = now
        if questionResponse.validForSubmission():
            questionResponse.save() # Required : To save the newly created questionResponse
            questionResponse.option.clear()
            for op in options:
                questionResponse.option.add(op)

            questionResponse.save()
            response_data['status'] = SUCCESS
            response_data['status_text'] = status_text[SUCCESS]
            
        else:
            quizResponse.activeStatus = False
            quizResponse.save()
            response_data['status'] = TIMES_UP
            response_data['status_text'] = status_text[TIMES_UP]

    else :
        response_data['status'] = NOTHING_TO_POST
        response_data['status_text'] = status_text[NOTHING_TO_POST]
    return JsonResponse(response_data)


@csrf_exempt
def ResetQuestion(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST
        email = data.get("email")
        questionId = data.get("questionId")
        
        #Getting the User
        try:
            user = User.objects.get(email=email)
        except:
            response_data['status'] = USER_NOT_FOUND
            response_data['status_text'] = status_text[USER_NOT_FOUND]
            return JsonResponse(response_data)

        #Getting the Quiz
        try:
            quiz = Quiz.objects.get(activeStatus = True)  
        except:
            response_data['status'] = NO_ACTIVE_QUIZ
            response_data['status_text'] = status_text[NO_ACTIVE_QUIZ]
            return JsonResponse(response_data)
        
        #Checking if the quizResponse of the user is valid or not
        try:
            quizResponse = QuizResponse.objects.get(user=user, quiz=quiz)
            if not quizResponse.activeStatus:
                response_data["status"] = RESPONSE_ALREADY_SUBMITTED
                response_data["status_text"] = status_text[RESPONSE_ALREADY_SUBMITTED]
                return JsonResponse(response_data)
        except:
            response_data['status'] = RESPONSE_NOT_FOUND
            response_data['status_text'] = status_text[RESPONSE_NOT_FOUND]
            return JsonResponse(response_data)

        #Getting the question to reset
        try:
            question = Questions.objects.get(questionId=questionId)
        except:
            response_data['status'] = INVALID_QUESTION
            response_data['status_text'] = status_text[INVALID_QUESTION]
            return JsonResponse(response_data)

        now = timezone.now()
        #Resetting the Response if it is valid (i.e. answered within the time limit)
        try:
            questionResponse = quizResponse.questionresponse_set.get(question=question, quizResponse=quizResponse)

            prevTime = questionResponse.responseTime
            
            questionResponse.responseTime = now
            questionResponse.save()
            if questionResponse.validForSubmission():
                questionResponse.delete()
                response_data['status'] = SUCCESS
                response_data['status_text'] = status_text[SUCCESS]
            else:
                questionResponse.responseTime = prevTime
                questionResponse.save()
                quizResponse.activeStatus = False
                quizResponse.save()
                response_data['status'] = TIMES_UP
                response_data['status_text'] = status_text[TIMES_UP]
        except:
            response_data['status'] = QUESTION_NOT_ATTEMPTED
            response_data['status_text'] = status_text[QUESTION_NOT_ATTEMPTED]
    else:
        response_data['status'] = NOTHING_TO_POST
        response_data['status_text'] = status_text[NOTHING_TO_POST]
    return JsonResponse(response_data)


@csrf_exempt
def FinalSubmit(request):
    response_data = {}
    if request.method == 'POST':
        data = request.POST
        email = data.get("email")
        
        #Getting the User
        try:
            user = User.objects.get(email=email)
        except:
            response_data['status'] = USER_NOT_FOUND
            response_data['status_text'] = status_text[USER_NOT_FOUND]
            return JsonResponse(response_data)

        #Getting the Quiz
        try:
            quiz = Quiz.objects.get(activeStatus = True)  
        except:
            response_data['status'] = NO_ACTIVE_QUIZ
            response_data['status_text'] = status_text[NO_ACTIVE_QUIZ]
            return JsonResponse(response_data)
        
        #Checking if the quizResponse of the user is valid or not
        try:
            quizResponse = QuizResponse.objects.get(user=user, quiz=quiz)
            quizResponse.activeStatus = False
            quizResponse.save()
            response_data["status"] = SUCCESS
            response_data["status_text"] = status_text[SUCCESS]
            return JsonResponse(response_data)
        except:
            response_data['status'] = RESPONSE_NOT_FOUND
            response_data['status_text'] = status_text[RESPONSE_NOT_FOUND]
            return JsonResponse(response_data)

    else:
        response_data['status'] = NOTHING_TO_POST
        response_data['status_text'] = status_text[NOTHING_TO_POST]
    return JsonResponse(response_data)


#Gives the Questions/Options for the quiz
def getQuizData(quizId, email):
    response = {}
    try:
        quiz = Quiz.objects.get(quizId=quizId)
        user = User.objects.get(email=email)
        # quizResponse = QuizResponse.objects.get(user=user, quiz = quiz)

        questionIdsSC = Questions.objects.filter(quiz=quiz, questionType='sc').values_list('questionId', flat=True)
        questionIdsMC = Questions.objects.filter(quiz=quiz, questionType='mc').values_list('questionId', flat=True)

       # questionsSC = random.sample(questionIdsSC, 10)
       # questionsMC = random.sample(questionIdsMC, 10)

        questionsSC = Questions.objects.filter(questionId__in = questionIdsSC)
        questionsMC = Questions.objects.filter(questionId__in = questionIdsMC)

       # for question in questionsSC:
       #     quizResponse.questions.add(question)
       # for question in questionsMC:
       #     quizResponse.questions.add(question)

        questionArraySC = []
        for question in questionsSC:
            questionobject = {}

            questionobject['question'] = question.questionTitle
            questionobject['id'] = question.questionId

            options=[]
            optionIds=[]
            for option in question.options_set.all():
                options.append(option.optionQuote)
                optionIds.append(option.optionId)

            questionobject['option'] = options
            questionobject['optionID'] = optionIds

            questionArraySC.append(questionobject)

        questionArrayMC = []
        for question in questionsMC:
            questionobject = {}

            questionobject['question'] = question.questionTitle
            questionobject['id'] = question.questionId

            options=[]
            optionIds=[]

            for option in question.options_set.all():
                options.append(option.optionQuote)
                optionIds.append(option.optionId)

            questionobject['option'] = options
            questionobject['optionID'] = optionIds

            questionArrayMC.append(questionobject)

        response['single'] = questionArraySC
        response['multiple'] = questionArrayMC
        total = len(questionArraySC) + len(questionArrayMC)
        response['ids'] = total
        response['singleIds'] = len(questionArraySC)
        response['multipleIds'] = len(questionArrayMC)
        
        return response
    except:
        return None

#REGISTER / LOGIN
def HomeView(request):
    if request.method =='GET':
        template_name = 'base.html'
        return render(request, template_name, {'user' : request.user})


@login_required(login_url = "/login")
def DashboardView(request):
    if request.method =='GET':
        template_name = 'index.html'
        return render(request, template_name, {'user_id' : request.user.email})


def AboutView(request):
    if request.method =='GET':
        template_name = 'registration/about.html'
        return render(request, template_name)   


def IndexView(request):
    if request.method =='GET':
        template_name = 'registration/index.html'
        return render(request, template_name)
    

def LoginView(request):
    if request.user.is_authenticated():
        return redirect('/')

    template_name = 'registration/login.html'
    if request.method == "POST":
        post = request.POST
        email = post['email']
        password = post['password']
        username = getUsername(email)
        user = authenticate(username=username, email=email, password=password)
        if user is not None:

            if user.is_active:
                login(request,user)
                return redirect('/')
            else:
                messages.warning(request, "You can login only when the quiz starts.", fail_silently=True)
                return redirect('/login')
        else:
            messages.error(request,'Invalid Credentials',fail_silently=True)
            return render(request,template_name,{})
    else:
        return render(request,template_name)


@login_required(login_url = "/login")
def LogoutView(request):
    logout(request)
    return redirect('/')


def RegistrationView(request):
    if request.user.is_authenticated():
        return redirect('/')

    template_name = 'registration/registration.html'
    context = {
            'all_colleges':College.objects.filter(isValid = True),
    }
    
    if request.method == "POST":
        post = request.POST
        email = post.get('email')
        email = email.lower()
        username = getUsername(email)
        if username == "ERROR":
            messages.warning(request, "Enter a valid email address.", fail_silently=True)
            return render(request,template_name,context)

        if len(username) > 30 or len(username) <= 0:
            messages.warning(request, "Email address is too long. Register with a different email address.", fail_silently=True)
            return render(request,template_name,context)
        
        password1 = post.get('password')
        password2 = post.get('repassword')
        if password1 != password2:
            messages.warning(request, "Passwords did not match.", fail_silently=True)
            return render(request,template_name,context)
        if len(password1) < 5:
            messages.warning(request, "Enter a password having atleast 5 characters.", fail_silently=True)
            return render(request,template_name,context)
        
        try:
            already_a_user = User.objects.get(username=username)
        except:#unique user.
            already_a_user = False

        if not already_a_user:#create new User instance.
##            try:
                user = User.objects.create_user(username=username,email=email)

                first_name = post.get('first_name')
                last_name = post.get('last_name')
                user.first_name = first_name
                user.last_name = last_name

                user.is_active = False #Can login when the quiz starts
                
                user.set_password(password1)
                user.save()
                
                userprofile = UserProfile.objects.create(user=user)
                try:
                    college = College.objects.get(collegeName=post.get('college'))
                except:
                    clgname=post.get('college')
                    if clgname is None:
                        clgname = ""
                    clgname=clgname.strip()
                    if clgname == "":
                        messages.warning(request, "Enter a valid College!", fail_silently=True)
                        user.delete()
                        return render(request,template_name,context)
                    college = College.objects.create(collegeName = clgname)


                year = post.get('year')
                mobile_number = post.get('mobile_number')

                userprofile.college = college
                userprofile.year = year
                userprofile.mobile_number = mobile_number


                #VALIDATION                
                first_name = first_name.strip()
                if year is None:
                    year = ""
                mobile_number = mobile_number.strip()

                #Checking an empty field
                if first_name == "" or year == "" or mobile_number == "":
                    messages.warning(request, "Form is not valid. Make sure you fill ALL the fields correctly!", fail_silently=True)
                    if not college.isValid:
                        college.delete()
                    user.delete()
                    return render(request,template_name,context)

                #Checking the length of mobile number
                if not(len(mobile_number) == 10 and mobile_number.isdigit()):
                    messages.warning(request, "Enter valid mobile number!", fail_silently=True)
                    if not college.isValid:
                        college.delete()
                    user.delete()
                    return render(request,template_name,context)

                #TODO
                #SheetUpdate(caprofile)
                messages.success(request, 'Successfully Registered.', fail_silently=True)
                userprofile.save()
                return redirect('/register')
##            except:
##                messages.warning(request, "Enter a valid form!", fail_silently=True)
##                #if not college.isValid:
##                #    college.delete()
##                user.delete()
##                return render(request,template_name,context)
        else:#already a user.
            messages.warning(request, "Email already registered!", fail_silently=True)
            return render(request,template_name,context)

    else:#request.method == "GET"
        return render(request,template_name,context)


#USE THIS FUNCTION TO CONVERT THE EMAIL TO USERNAME(having less than 30 characters)
def getUsername(email):
    try:
        index = email.index('@')
    except:
        return 'ERROR'
    emailCode = changeBase(email[:index], 41, 94)
    
    domain = email[index+1:]
    domainCode = getDomainCode(domain)

    if emailCode == 'ERROR' or domainCode == 'ERROR':
        return 'ERROR'
    
    answer = emailCode + domainCode
    return answer


def getDomainCode(domain):
    try:
        domain = Domain.objects.get(domainName=domain)
    except:
        domain = Domain.objects.create(domainName = domain)
        domainId = domain.domainId
        domainCode = changeBase(str(domainId), 41, 94)
        if domainCode == 'ERROR':
            return 'ERROR'
        if len(domainCode) == 1:
            domainCode = "0" + domainCode
        domain.domainCode = domainCode
        domain.save()
    return domain.domainCode;

    
def changeBase(innitvar, basevar, convertvar):
    # Create a symbol-to-value table.
    SY2VA = {'0': 0,
             '1': 1,
             '2': 2,
             '3': 3,
             '4': 4,
             '5': 5,
             '6': 6,
             '7': 7,
             '8': 8,
             '9': 9,
             'a': 10,
             'b': 11,
             'c': 12,
             'd': 13,
             'e': 14,
             'f': 15,
             'g': 16,
             'h': 17,
             'i': 18,
             'j': 19,
             'k': 20,
             'l': 21,
             'm': 22,
             'n': 23,
             'o': 24,
             'p': 25,
             'q': 26,
             'r': 27,
             's': 28,
             't': 29,
             'u': 30,
             'v': 31,
             'w': 32,
             'x': 33,
             'y': 34,
             'z': 35,
             '.': 36,
             '_': 37,
             '-': 38,
             '+': 39,
             '%': 40,
             '&': 41,
             "'": 42,
             '(': 43,
             ')': 44,
             '*': 45,
             '$': 46,
             ',': 47,
             '#': 48,
             '!': 49,
             '/': 50,
             ':': 51,
             ';': 52,
             '<': 53,
             '=': 54,
             '>': 55,
             '?': 56,
             '@': 57,
             '[': 58,
             '\\': 59,
             ']': 60,
             '^': 61,
             '"': 62,
             '`': 63,
             '{': 64,
             '|': 65,
             '}': 66,
             '~': 67,
             'A': 68,
             'B': 69,
             'C': 70,
             'D': 71,
             'E': 72,
             'F': 73,
             'G': 74,
             'H': 75,
             'I': 76,
             'J': 77,
             'K': 78,
             'L': 79,
             'M': 80,
             'N': 81,
             'O': 82,
             'P': 83,
             'Q': 84,
             'R': 85,
             'S': 86,
             'T': 87,
             'U': 88,
             'V': 89,
             'W': 90,
             'X': 91,
             'Y': 92,
             'Z': 93}

    # Take a string and base to convert to.
    # Allocate space to store your number.
    # For each character in your string:
    #     Ensure character is in your table.
    #     Find the value of your character.
    #     Ensure value is within your base.
    #     Self-multiply your number with the base.
    #     Self-add your number with the digit's value.
    # Return the number.
    
    integer = 0
    answer = 'ERROR'
    for character in innitvar:
        try:
            assert character in SY2VA
            value = SY2VA[character]
            assert value < basevar
        except:
            return answer
        integer *= basevar
        integer += value

    # Create a value-to-symbol table.
    VA2SY = dict(map(reversed, SY2VA.items()))

    # Take a integer and base to convert to.
    # Create an array to store the digits in.
    # While the integer is not zero:
    #     Divide the integer by the base to:
    #         (1) Find the "last" digit in your number (value).
    #         (2) Store remaining number not "chopped" (integer).
    #     Save the digit in your storage array.
    # Return your joined digits after putting them in the right order.

    answer = ""
    array = []
    while integer:
        integer, value = divmod(integer, convertvar)
        array.append(VA2SY[value])
    answer = ''.join(reversed(array))

    return answer


def editUsernames():
    users = User.objects.all()
    for user in users:
        if not user.is_superuser:
            email = user.email
            username = getUsername(email)
            user.username = username
            user.save()

def activateUsers():
    users = User.objects.all()
    for user in users:
        user.is_active = True
        user.save()


def createSuperuser(username, password):
    try:
        user = User.objects.get(username = username)
        print("Superuser already exists.")
    except:
        user = User.objects.create(username = username)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("New superuser created.")

def createUser(email, password):
    username = getUsername(email)
    if username == "ERROR":
        print("Enter Valid Username")
        return
    try:
        user = User.objects.get(username=username)
        print("User already exists.")
    except:
        user = User.objects.create(username = username, email=email)
        user.set_password(password)
        user.save()
        print("New user created.")


def activateQuiz(quizId):
    try:
        quiz = Quiz.objects.get(quizId=quizId)

        deactivateQuizzes()
        quiz.activeStatus = True
        quiz.save()
        print("Quiz ID " + str(quizId) + " activated.")
    except:
        print("Quiz Does not Exist.")

def deactivateQuizzes():
    quizzes = Quiz.objects.all()
    for quiz in quizzes:
        quiz.activeStatus = False
        quiz.save()
    print("Quizzes deactivated.")