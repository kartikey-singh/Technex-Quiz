from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import *


class UserAdmin(UserAdmin):

    def name(obj):
        return "%s %s" % (obj.first_name, obj.last_name)


    def college(obj):
        return "%s" % obj.userprofile.college

    def mobile_number(obj):
        return "%s" % obj.userprofile.mobile_number

    name.short_description = 'Name'
    list_display = ('email','username', name, college, mobile_number)
    

admin.site.register(UserProfile)
admin.site.register(College)

admin.site.register(Quiz)
admin.site.register(Questions)
admin.site.register(Options)
admin.site.register(QuizResponse)
admin.site.register(QuestionResponse)
