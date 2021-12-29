from django.db import models
from datetime import date
 
from django.urls import reverse
import datetime
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Answer, Question, Choice
 
#Модели 
class BsUsers(models.Model):
    session_id = models.SlugField(max_length=160, unique=True)
    status = models.PositiveIntegerField("status", default=0)
    sex = models.PositiveIntegerField("sex", default=0)
    age = models.PositiveIntegerField("age", default=0)
    family = models.PositiveIntegerField("family", default=0)
    children = models.PositiveIntegerField("children", default=0)
    repair_status = models.PositiveIntegerField("repair_status", default=0)
    repair_when_finish = models.PositiveIntegerField("repair_when_finish", default=0)
    repair_object_other = models.PositiveIntegerField("repair_object_other", default=0)
    have_cottage = models.PositiveIntegerField("have_cottage", default=0)
    plan_cottage_works = models.PositiveIntegerField("plan_cottage_works", default=0)
    who_worker = models.PositiveIntegerField("who_worker", default=0)
    who_chooser = models.PositiveIntegerField("who_chooser", default=0)
    who_buyer = models.CharField("who_buyer", max_length=150)
    where_buy_other = models.CharField("where_buy_other", max_length=150)
    shop_name = models.CharField("shop_name", max_length=150)
    fio = models.CharField("fio", max_length=150)
    phone = models.CharField("phone", max_length=150)
    email = models.EmailField("email", max_length=150)
    distance = models.PositiveIntegerField("distance", default=0)
    city_id = models.PositiveIntegerField("city_id", default=0)
    city_other = models.IntegerField("city_other", default=0)
    money = models.IntegerField("money", default=0)
    created_at = models.DateTimeField("created_at", default=datetime.datetime.now())
    updated_at = models.DateTimeField("updated_at", default=datetime.datetime.now())
    family_type = models.PositiveIntegerField("family_type", default=0)
 
    class Meta:
        verbose_name = "Запись опроса"
        verbose_name_plural = "Запись опроса"
 
 
 
 
 
#Регистрация пользователей
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
 
    class Meta:
        model = User
        fields = ('Имя пользователя', 'Имя', 'Email')
 
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
 
    def register(request):
        if request.method == 'POST':
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                # Create a new user object but avoid saving it yet
                new_user = user_form.save(commit=False)
                # Set the chosen password
                new_user.set_password(user_form.cleaned_data['password'])
                # Save the User object
                new_user.save()
                return render(request, 'account/register_done.html', {'new_user': new_user})
        else:
            user_form = UserRegistrationForm()
        return render(request, 'account/register.html', {'user_form': user_form})
 
 
 
#Опрос пользователей 
class ChoiceSerializer(serializers.ModelSerializer):
    percent = serializers.SerializerMethodField()
 
    class Meta:
        model = Choice
        fields = ['pk', 'title', 'points', 'percent', 'lock_other', ]
 
    def get_percent(self, obj):
        total = Answer.objects.filter(question=obj.question).count()
        current = Answer.objects.filter(question=obj.question, choice=obj).count()
        if total != 0:
            return float(current * 100 / total)
        else:
            return float(0)
 
 
class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, source='choice_set', )
 
    class Meta:
        model = Question
        fields = ['pk', 'title', 'choices', 'max_points', ]
 
 
class AnswerSerializer(serializers.Serializer):
    answers = serializers.JSONField()
 
    def validate_answers(self, answers):
        if not answers:
            raise serializers.Validationerror("Answers must be not null.")
        return answers
 
    def save(self):
        answers = self.data['answers']
        user = self.context.user
        for question_id, in answers:  # тут наверное лишняя запятая , ошибка в оригинальном коде
            question = Question.objects.get(pk=question_id)
            choices = answers[question_id]
            for choice_id in choices:
                choice = Choice.objects.get(pk=choice_id)
                Answer(user=user, question=question, choice=choice).save()
                user.is_answer = True
                user.save()
