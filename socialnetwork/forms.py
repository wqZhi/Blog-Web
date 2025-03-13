from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from socialnetwork.models import Post, Profile
# from django.utils.timezone import now

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more than one field
    # Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function
        # Gets a dictionary of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data



class RegisterForm(forms.Form):
    username   = forms.CharField(max_length=20,
                                 widget=forms.TextInput(attrs={'id': 'id_username'}))
    password1  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput(attrs={'id': 'id_password'}))
    password2  = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput(attrs={'id': 'id_confirm_password'}))
    email      = forms.CharField(max_length=50,
                                 widget=forms.EmailInput(attrs={'id': 'id_email'}))
    first_name = forms.CharField(max_length=20,
                                 widget=forms.TextInput(attrs={'id': 'id_first_name'}))
    last_name  = forms.CharField(max_length=20,
                                 widget=forms.TextInput(attrs={'id': 'id_last_name'}))

    # Customizes form validation for properties that apply to more than one field.
    # Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function
        # Gets a dictionary of cleaned data as a result
        cleaned_data = super().clean()

        # Add an extra validation
        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            # Generates a form error (non-field error)
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    
    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            # Generates a field error specific to the field (username here)
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data dictionary
        return username



MAX_UPLOAD_SIZE = 2500000
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio_input_text', 'picture')
        widgets = {
            'bio_input_text': forms.Textarea(attrs={'id':'id_bio_input_text', 'rows':'3'}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture'}),
        }
        labels={
            'bio': "",
            'picture': "Upload image"
        }

    def clean_bio_input_text(self):
        text = self.cleaned_data['bio_input_text']
        if len(text) > 200:
            raise forms.ValidationError('Bio must be 200 characters or fewer.')
        return text
    
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(f'File too big (max size is {MAX_UPLOAD_SIZE} bytes)')
        return picture
    


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('post_input_text',)
        widgets = {
            'post_input_text': forms.Textarea(attrs={
                'id': 'id_post_input_text',
                'class': 'post-input',
                'rows': 3,
                'placeholder': 'Write your post here...'
            })
        }
    
    def clean_post_input_text(self):
        text = self.cleaned_data['post_input_text']
        if len(text) > 200:
            raise forms.ValidationError('Bio must be 200 characters or fewer.')
        return text