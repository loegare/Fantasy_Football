from django import forms

from .models import Topic


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5,
                                                           'placeholder': 'Sup?'}),
                              max_length=4000,
                              help_text='The max length of text is 4k')

    class Meta:
        model = Topic
        fields = ['subject', 'message']
