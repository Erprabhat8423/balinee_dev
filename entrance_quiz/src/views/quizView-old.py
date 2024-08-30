from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from apps.src.models.models import *
from utils import *
from datetime import date, timedelta, time
from datetime import datetime as dt
from django.views.decorators.csrf import csrf_exempt
import json


# Create your views here.
@csrf_exempt
def registration(request):
    if request.method == "GET":
        template = 'quiz/index.html'
        return render(request, template)
    
    if request.method == "POST":
        if request.POST["contact"] == '':  
            return HttpResponse({'message': 'Please provide Contact Number', 'response_code': 400}, status=400)
        else:
            contact = request.POST["contact"]

        # otp = generateEntranceOTP()
        otp = '1'

        if TblEntranceRegistration.objects.filter(contact=contact).exists():
            if TblEntranceOtp.objects.filter(student_contact=contact).exists():
                TblEntranceOtp.objects.filter(student_contact=contact).delete()

            entrance = TblEntranceOtp()
            entrance.student_contact = contact
            entrance.otp = otp
            entrance.save()

            message = "OTP for login verification " + str(otp)
            admin_msg = "OTP for login verification " + str(otp) +" for "+ getModelColumnByColumnId(TblEntranceRegistration, 'contact', contact, 'student_name')

            print("Messages: ", message)
            print("Admin Messages: ", admin_msg)
            # sendSMS('BGIVNS', contact, message)
            # sendSMS('BGIVNS', '7704987777', admin_msg)

            return HttpResponse("Registration Mobile number does exists", status = 200)
        else:
            res = HttpResponse("Registration Mobile number does not exists", content_type='application/json')
            res.status_code = 400
            return res


def validatingOTP(request):
    if request.method == 'GET':
        if request.GET["otp"] == '':
            return Response({'message': 'Please provide OTP', 'response_code': 400}, status=400)
        else:
            otp = request.GET["otp"]
        
        if request.GET["contact"] == '':
            return Response({'message': 'Please provide Contact Number', 'response_code': 400}, status=400)
        else:
            contact = request.GET["contact"]
        
        if TblEntranceOtp.objects.filter(student_contact = contact, otp = otp).exists():
            candidate_id = getModelColumnByColumnId(TblEntranceRegistration, 'contact', contact, 'id')
            if not TblEntranceQuiz.objects.filter(candidate_id = candidate_id).exists():
                quiz = TblEntranceQuiz()
                quiz.candidate_id = candidate_id
                quiz.result = 0
                quiz.time_left = time(hour=1)
                quiz.save()

                template = 'quiz/terms.html'
                context = {}
                context['candidate_id'] = candidate_id
                context['contact']      = contact
                return render(request, template, context)

            elif TblEntranceQuiz.objects.filter(candidate_id=candidate_id).exists():
                quiz = TblEntranceQuiz()
                candidate_quest = TblEntranceQuiz.objects.filter(candidate_id=candidate_id).last()
                time_str = str(candidate_quest.time_left)
                hh, mm, ss = time_str.split(':')
                time_left = int(hh) * 3600 + int(mm) * 60 + int(ss)

                if candidate_quest.question_answers is not None or candidate_quest.question_answers != "":
                    all_questions = []
                    for question in candidate_quest.question_answers:
                        each_ques = TblQuizQuestionnaire.objects.filter(id=question['question_id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]
                        all_questions.append(each_ques)
                ques = candidate_quest.question_answers[0]
                first_ques = TblQuizQuestionnaire.objects.filter(id=ques['question_id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]
                
                context = {}
                context['candidate_id']     = candidate_id
                context['total_questions']  = len(all_questions)
                context['all_questions']    = all_questions
                context['candidate_quest']  = candidate_quest
                context['first_question']   = first_ques
                context['attempts']         = ques
                context['pos']              = 1
                context['time_left']        = time_left

                template = 'quiz/quesfirst.html'
                return render(request, template, context)

        else:
            res = HttpResponse("Invalid OTP", content_type='application/json')
            res.status_code = 400
            return res


@csrf_exempt
def ajaxQuizQuestion(request):
    if request.method == "POST":
        index = int(request.POST['position']) - 1
        candidate_id = request.POST['candidate_id']
        id = int(request.POST['id'])
        answer = request.POST['answer']

        if TblEntranceQuiz.objects.filter(candidate_id=candidate_id).exists():
                candidate_quest = TblEntranceQuiz.objects.filter(candidate_id=candidate_id).last()
                time_str = str(candidate_quest.time_left)
                hh, mm, ss = time_str.split(':')
                time_left = int(hh) * 3600 + int(mm) * 60 + int(ss)

                if candidate_quest.question_answers is not None or candidate_quest.question_answers != "":
                    all_questions = []
                    for question in candidate_quest.question_answers:
                        each_ques = TblQuizQuestionnaire.objects.filter(id=question['question_id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]
                        all_questions.append(each_ques)
                ques = candidate_quest.question_answers[index]

                # for each_question in candidate_quest.question_answers:
                #     if each_question['question_id'] == id:
                #         print("Found Question: ", each_question)

                first_ques = TblQuizQuestionnaire.objects.filter(id=ques['question_id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]

                context = {}
                context['candidate_id']     = candidate_id
                context['total_questions']  = len(all_questions)
                context['all_questions']    = all_questions
                context['candidate_quest']  = candidate_quest
                context['first_question']   = first_ques
                context['time_left']        = time_left
                context['attempts']         = ques
                context['pos']              = index+1

                template = 'quiz/ajax-quest.html'
                return render(request, template, context)

def quizTerm(request):
    if request.method == "GET":
        context = {}
        context['candidate_id'] = request.POST['candidate_id']
        template = 'quiz/terms.html'
        return render(request, template, context)

@csrf_exempt
def quizStart(request):
    if request.method == "POST":

        subjects = TblSubjects.objects.filter().values("id").order_by("?")
        all_questions = []
        all_allocation = []

        for each_subject in subjects:
            each_subject_question = TblQuizQuestionnaire.objects.filter(subject_id = each_subject['id']).order_by("?")[:10].values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')
            for each_question in each_subject_question:
                all_questions.append(each_question)

        for each_quest in all_questions:
            quiz_ques_allocation = {}
            quiz_ques_allocation['question_id'] = each_quest['id']
            quiz_ques_allocation['question']    = each_quest['question']
            quiz_ques_allocation['answer']      = 0
            all_allocation.append(quiz_ques_allocation)

        if TblEntranceQuiz.objects.filter(candidate_id=request.POST['candidate_id']).exists():
            candidate_quest_alloc = TblEntranceQuiz.objects.get(candidate_id=request.POST['candidate_id'])
            if candidate_quest_alloc.question_answers is None:
                candidate_quest_alloc.question_answers = all_allocation
                candidate_quest_alloc.save()

        template = 'quiz/totalquestion.html'
        context = {}
        context['candidate_id'] = request.POST['candidate_id']
        return render(request, template, context)

def quizQuestions(request):
    if request.method == "GET":
        candidate_id = request.GET['candidate_id']
        # candidate_id = 3
        subjects = TblSubjects.objects.filter().values("id").order_by("?")
        all_questions = []

        if TblEntranceQuiz.objects.filter(candidate_id = candidate_id).exists():
            registered_candidate = TblEntranceQuiz.objects.get(candidate_id = candidate_id)
            registered_candidate.quiz_start_datetime = datetime.now()
            registered_candidate.save()
        
        if TblEntranceQuiz.objects.filter(candidate_id=candidate_id).exists():
            candidate_quest = TblEntranceQuiz.objects.filter(candidate_id=candidate_id).last()
            time_str = str(candidate_quest.time_left)
            hh, mm, ss = time_str.split(':')
            time_left = int(hh) * 3600 + int(mm) * 60 + int(ss)

            if candidate_quest.question_answers is not None or candidate_quest.question_answers != "":
                for question in candidate_quest.question_answers:
                    each_ques = TblQuizQuestionnaire.objects.filter(id=question['question_id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]
                    all_questions.append(each_ques)
            
            # first_ques = candidate_quest.question_answers[0]
            first_ques = TblQuizQuestionnaire.objects.filter(id=all_questions[0]['id']).values('id', 'question', 'option_1', 'option_2', 'option_3', 'option_4')[0]

        context = {}
        context['candidate_id']     = candidate_id
        context['total_questions']  = len(all_questions)
        context['all_questions']    = all_questions
        context['candidate_quest']  = candidate_quest
        context['time_left']        = time_left
        context['attempts']         = first_ques
        context['first_question']   = first_ques
        context['pos']              = 1

        template = 'quiz/quesfirst.html'
        return render(request, template, context)

@csrf_exempt
def quizSave(request):
    if request.method == "POST":
        candidate_id    = request.POST['candidate_id']
        selection       = request.POST['all_answers']
        time_left       = request.POST['time_left']
        position        = int(request.POST['position'])
        answer          = int(request.POST['answer'])
        # time_left       = "00:"+time_left

        parsed_selection = json.loads(selection)

        if time_left != "00:00:00":
            if TblEntranceQuiz.objects.filter(candidate_id = candidate_id).exists():
                registered_candidate = TblEntranceQuiz.objects.get(candidate_id = candidate_id)
                registered_candidate.time_left = time_left

                # for each_allocated in registered_candidate.question_answers:
                #     for each_selected in parsed_selection:
                #         if each_allocated['question_id'] == each_selected['question_id']:

                #             if 'selected_option' in each_selected:
                #                 if each_selected['selected_option'] != "":
                #                     each_allocated['answer'] = int(each_selected['selected_option'])
                #                 else:
                #                     each_allocated['answer'] = 0
                #             else:
                #                 each_allocated['answer'] = 0

                # for each_answer in registered_candidate.question_answers:
                #     print("Each: ", each_answer[position])

                # registered_candidate.question_answers[position]['answer'] = answer
                registered_candidate.question_answers = parsed_selection

                registered_candidate.updated_at = datetime.now()
                registered_candidate.save()

            return HttpResponse({'message': "Success"}, status=200)

@csrf_exempt
def quizSubmit(request):
    if request.method == "POST":
        candidate_id    = request.POST['candidate_id']
        selection       = request.POST['selections']
        time_left       = request.POST['time_left']

        parsed_selection = json.loads(selection)

        if TblEntranceQuiz.objects.filter(candidate_id = candidate_id).exists():
            registered_candidate = TblEntranceQuiz.objects.get(candidate_id = candidate_id)

            for each_allocated in registered_candidate.question_answers:
                for each_selected in parsed_selection:
                    if each_allocated['question_id'] == each_selected['question_id']:

                        if 'selected_option' in each_selected:
                            if each_selected['selected_option'] != "":
                                each_allocated['answer'] = int(each_selected['selected_option'])
                            else:
                                each_allocated['answer'] = 0
                        else:
                            each_allocated['answer'] = 0

            registered_candidate.quiz_end_datetime  = datetime.now()
            registered_candidate.result             = 3
            registered_candidate.time_left          = time_left
            registered_candidate.save()

        return HttpResponse({'message': "Success"}, status=200)


def declineTerms(request):
    if request.method == "GET":
        candidate_id = request.GET['candidate_id']
        TblEntranceQuiz.objects.filter(candidate_id = candidate_id).delete()
        return HttpResponse({'message': "Success"}, status=200)