from django import forms
from .models import Finance, Expense, BankAccount, Attendance

class DateInput(forms.DateInput):
    input_type = 'date'

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'service', 'service_type', 'adult_count', 'children_count', 'first_timers_count']
        widgets = {
            'date': DateInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'service': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'service_type': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'adult_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'children_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'first_timers_count': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
        }


class IncomeForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Tithe', 'Tithe'),
        ('Offering', 'Offering'),
        ('First Fruit', 'First Fruit'),
        ('Thanksgiving', 'Thanksgiving'),
        ('Donation', 'Donation'),
        ('Project Support', 'Project Support'),
        ('Seed', 'Seed'),
        ('Welfare Contribution', 'Welfare Contribution'),
        ('Other', 'Other'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}))
    
    class Meta:
        model = Finance
        fields = ['date', 'category', 'amount', 'member', 'description', 'ministry', 'bank_account']
        widgets = {
            'date': DateInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'member': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all', 'rows': 3}),
            'ministry': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'bank_account': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
        }

class ExpenseForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Salaries', 'Salaries'),
        ('Honorarium', 'Honorarium'),
        ('Maintenance', 'Maintenance'),
        ('Utilities', 'Utilities'),
        ('Equipment', 'Equipment'),
        ('Welfare', 'Welfare'),
        ('Transport', 'Transport'),
        ('Fuel/Diesel', 'Fuel/Diesel'),
        ('Media/Tech', 'Media/Tech'),
        ('Other', 'Other'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}))

    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'description', 'authorized_by', 'bank_account']
        widgets = {
            'date': DateInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all', 'rows': 3}),
            'authorized_by': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
            'bank_account': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-transparent focus:ring-2 focus:ring-brand-navy outline-none transition-all'}),
        }
