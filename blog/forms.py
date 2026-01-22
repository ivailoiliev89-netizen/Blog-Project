from django import forms
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'})
        }
        labels = {'body': ''}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category', 'tags']
        widgets = {
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'custom-tag-list'}),
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
        }
