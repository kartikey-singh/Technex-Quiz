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


@csrf_exempt
def StartTest(request):
    response_data = {'status' : 0}
    data = request.POST
    email = data.get("email")
    # email = "navpun31@gmail.com"
    try:
        user = User.objects.get(email=email)
        quiz = Quiz.objects.get(activeStatus = True)
                        
        quizId = quiz.quizId
        now = timezone.now()
        try:
            quizResponse = QuizResponse.objects.get(user=user, quiz=quiz)
        except:
            quizResponse = QuizResponse.objects.create(user=user, quiz=quiz, timeOfAttempt=now)
            quizResponse.save()

        try:
            response_data = getQuizData(quizId, email)
            response_data["s_time"] = quiz.startTime
            response_data["e_time"] = quiz.endTime
            response_data["u_time"] = quizRespone.timeOfAttempt
            if response_data is not None:
                response_data["status"] = 1 # Success
            else:
                response_data["status"] = 3 # Error Adding Data
        except:
            response_data["status"] = 2 # Error Adding Data
    except:
        response_data["status"] = 0 # No User/Active Quiz Found
        return JsonResponse(response_data)
    return JsonResponse(response_data)

@csrf_exempt
def SubmitQuestion(request):
    response = {}
    if request.method == 'POST':
        data = request.POST
        email = data.get("email")
        questionId = data.get("questionId")
        question = Questions.objects.get(questionId=questionId)
        
        optionIds = data.get("optionIds")
        options = Options.objects.filter(optionId__in = optionIds)

        try:
            quiz = Quiz.objects.get(activeStatus = True)  
        except:
            response_data['status'] = 0 # No Active Quiz Found / Quiz has ended
            return JsonResponse(response_data)

        try:
            user = User.objects.get(email=email)
        except:
            response_data['status'] = 1 # No User Found
            return JsonResponse(response_data)

        now = timezone.now()
        try:
            quizResponse = QuizResponse.objects.get(user=user)
        except:
            response_data['status'] = 2 # Quiz Response Not Found
            return JsonResponse(response_data)

        try:
            questionResponse = quizResponse.questionresponse_set.get(question=question, quizResponse=quizResponse)
        except:
            questionResponse = QuestionResponse(question=question,quizResponse=quizResponse)
        
        questionResponse.responseTime = now
        if questionResponse.validForSubmission():
            questionResponse.option.clear()
            for op in options:
                questionResponse.option.add(op)

            questionResponse.save()
            response_data['status'] = 3 # Success
            
        else:
            response_data['status'] = 4 # Quiz has ended

        return JsonResponse(response_data)


@csrf_exempt
def ResetQuestion(request):
    response = {}
    if request.method == 'POST':
        data = request.POST
        email = data.get("email")
        questionId = data.get("questionId")

        try:
            quiz = Quiz.objects.get(activeStatus = True)  
        except:
            response_data['status'] = 0 # No Active Quiz Found / Quiz has ended
            return JsonResponse(response_data)

        try:
            user = User.objects.get(email=email)
        except:
            response_data['status'] = 1 # No User Found
            return JsonResponse(response_data)

        try:
            quizResponse = QuizResponse.objects.filter(user=user)
        except:
            response_data['status'] = 2 # Quiz Response Not Found
            return JsonResponse(response_data)

        try:
            questionResponse = quizResponse.questionresponse_set.filter(question=question, quizResponse=quizResponse)
            questionResponse.delete()
            response_data['status'] = 3 # Success
        except:
            response_data['status'] = 4 # Question Not Attempted

        return JsonResponse(response_data)


#Gives the Questions/Options for the quiz
def getQuizData(quizId, email):
    if 1:#try:
        response = {}

        quiz = Quiz.objects.get(quizId=quizId)
        user = User.objects.get(email=email)
        quizResponse = QuizResponse.objects.get(user=user, quiz = quiz)

        questionIdsSC = Questions.objects.filter(quiz=quiz, questionType='sc').values_list('questionId', flat=True)
        questionIdsMC = Questions.objects.filter(quiz=quiz, questionType='mc').values_list('questionId', flat=True)

##        questionsSC = random.sample(questionIdsSC, 10)
##        questionsMC = random.sample(questionIdsMC, 10)

        questionsSC = Questions.objects.filter(questionId__in = questionIdsSC)
        questionsMC = Questions.objects.filter(questionId__in = questionIdsMC)

##        for question in questionsSC:
##            quizResponse.questions.add(question)
##        for question in questionsMC:
##            quizResponse.questions.add(question)

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

        return response
    else: #except:
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

@login_required(login_url = "/login")
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
        email = user.email
        username = getUsername(email)
        user.username = username
        user.save()

def activateUsers():
    users = User.objects.all()
    for user in users:
        user.is_active = True
        user.save()
