from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Visitor, FollowUpLog
from people.models import Member
from django.utils import timezone

class VisitorListView(LoginRequiredMixin, ListView):
    model = Visitor
    template_name = 'outreach/visitor_list.html'
    context_object_name = 'visitors'

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-visit_date')
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains(q)) | 
                Q(last_name__icontains(q)) | 
                Q(phone__icontains(q)) |
                Q(email__icontains(q))
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get('status')
        # Boolean flags to simplify template logic
        context['status_is_new'] = status == 'new'
        context['status_is_pending'] = status == 'pending'
        context['status_is_converted'] = status == 'converted'
        context['status_is_lost'] = status == 'lost'
        return context

class VisitorCreateView(LoginRequiredMixin, CreateView):
    model = Visitor
    fields = ['first_name', 'last_name', 'email', 'phone', 'whatsapp_number', 'address', 'city', 
              'dob', 'gender', 'marital_status', 'visit_date', 'how_did_you_hear', 
              'invited_by', 'prayer_request', 'interest_in_membership']
    template_name = 'outreach/visitor_form.html'
    success_url = reverse_lazy('visitor-list')

class VisitorDetailView(LoginRequiredMixin, DetailView):
    model = Visitor
    template_name = 'outreach/visitor_detail.html'
    context_object_name = 'visitor'

class FollowUpCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        visitor = get_object_or_404(Visitor, pk=pk)
        FollowUpLog.objects.create(
            visitor=visitor,
            follow_up_type=request.POST.get('type'),
            notes=request.POST.get('notes'),
            handled_by=request.user
        )
        return redirect('visitor-detail', pk=pk)

class MigrateToMemberView(LoginRequiredMixin, View):
    def post(self, request, pk):
        visitor = get_object_or_404(Visitor, pk=pk)
        
        if visitor.status == 'converted':
            return redirect('visitor-detail', pk=pk)
            
        # Create new Member
        member = Member.objects.create(
            first_name=visitor.first_name,
            last_name=visitor.last_name,
            email=visitor.email,
            phone=visitor.phone,
            whatsapp_number=visitor.whatsapp_number,
            address=visitor.address,
            city=visitor.city,
            dob=visitor.dob,
            gender=visitor.gender,
            marital_status=visitor.marital_status,
            membership_date=timezone.now().date(),
            member_type='Member'
        )
        
        # Link and Update Visitor
        visitor.status = 'converted'
        visitor.converted_member = member
        visitor.save()
        
        return redirect('member-detail', pk=member.pk)
