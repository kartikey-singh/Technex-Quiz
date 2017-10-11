from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from django.utils import timezone

question_types = [
	('sc','Single Correct'),
	('mc','Multiple Correct'),
]

year_choices = [
	(None,'Year of study'),
	(1, 'First'),
	(2, 'Second'),
	(3, 'Third'),
	(4, 'Fourth'),
	(5,'Fifth'),
]

class Quiz(models.Model):
	quizId = models.AutoField(primary_key = True)
	name = models.CharField(max_length=50)
	description = models.TextField(null = True)
	duration = models.IntegerField(default = 30)
	startTime = models.DateTimeField(null = True)
	endTime = models.DateTimeField(null = True)
	activeStatus = models.BooleanField(default=False)
     
	def __str__(self):
		return 'QUIZ : %s' %(self.name)


class Questions(models.Model):
	questionId = models.AutoField(primary_key = True)
	quiz = models.ForeignKey(Quiz,null = True)
	questionType = models.CharField(max_length = 10, choices = question_types, default = 'sc')
	questionTitle = models.TextField()

	def __str__(self):
		return 'QUESTION : %s-%s' %(self.questionType, self.questionTitle)


class Options(models.Model):
	optionId = models.AutoField(primary_key = True)
	optionQuote = models.CharField(max_length = 250)
	question = models.ForeignKey(Questions,null = True)
	isCorrect = models.BooleanField(default=False)

	def __str__(self):
		return 'OPTION : %s - %s' %(self.optionQuote, self.question)


class QuizResponse(models.Model):
	responseId = models.AutoField(primary_key = True)
	quiz = models.ForeignKey(Quiz,null=True)
	user = models.ForeignKey(User,null=True)
	timeOfAttempt = models.DateTimeField(null = True)
	#questions = models.ManyToManyField(Questions,null = True)

	def __str__(self):
		return '%s - %s' %(self.user.email, self.quiz)

class QuestionResponse(models.Model):
	responseId = models.AutoField(primary_key = True)
	question = models.ForeignKey(Questions,null = True)
	quizResponse = models.ForeignKey(QuizResponse,null = True)
	responseTime = models.DateTimeField(null = True)
	option = models.ManyToManyField(Options,null = True)
	
	def __str__(self):
		return '%s - %s - OPTIONS : %s' %(self.quizResponse, self.question, " - ".join([op.optionQuote for op in self.option.all()]))
	
	def validForSubmission(self):
		minutes = self.quiz_response.quiz.duration
		quizEndTime = self.quizResponse.quiz.endTime

		now = self.responseTime
		#now = timezone.now()
		
		timediff = now - self.quiz_response.timeOfAttempt
		if timediff.total_seconds() > minutes*60 or now > quizEndTime:
			return False
		else:
			return True


class College(models.Model):
	collegeId = models.AutoField(primary_key = True)
	collegeName = models.CharField(max_length=250)
	isValid = models.BooleanField(default=False)

	def __str__(self):
		return '%s' %(self.collegeName)


class UserProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	mobile_number = models.BigIntegerField(null=True)
	college = models.ForeignKey(College,null = True)
	year = models.IntegerField(choices=year_choices,null=True,blank=True,default=1)

	def __str__(self):
		return '%s %s-%s' %(self.user.first_name, self.user.last_name, self.college)


class Domain(models.Model):
	domainId = models.AutoField(primary_key = True)
	domainName = models.CharField(max_length=250)
	domainCode = models.CharField(max_length=2, default="00")

	def __str__(self):
		return '%s' %(self.domainName)

