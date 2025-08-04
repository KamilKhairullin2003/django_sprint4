from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, User, Comment


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Ваша фамилия'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.come'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'password1',
                  'password2',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%d.%m.%YT%H:%M'),
                attrs={'type': 'datetime-local'}
            )
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
