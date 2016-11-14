"""
Utility functions for validating forms
"""
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.contrib.auth.tokens import default_token_generator

from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _
from django.template import loader

from django.conf import settings
from microsite_configuration import microsite
from util.password_policy_validators import (
    validate_password_length,
    validate_password_complexity,
    validate_password_dictionary,
)

import logging
#IITBombayX add and display team members
import re
from django.core.validators import RegexValidator,validate_integer


log=logging.getLogger("__name__")


class PasswordResetFormNoActive(PasswordResetForm):
    def clean_email(self):
        """
        This is a literal copy from Django 1.4.5's django.contrib.auth.forms.PasswordResetForm
        Except removing the requirement of active users
        Validates that a user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        #The line below contains the only change, removing is_active=True
        self.users_cache = User.objects.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD)
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(
            self,
            domain_override=None,
            subject_template_name='registration/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.html',
            use_https=False,
            token_generator=default_token_generator,
            from_email=settings.DEFAULT_FROM_EMAIL,
            request=None
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # This import is here because we are copying and modifying the .save from Django 1.4.5's
        # django.contrib.auth.forms.PasswordResetForm directly, which has this import in this place.
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                site_name = microsite.get_value(
                    'SITE_NAME',
                    settings.SITE_NAME
                )
            else:
                site_name = domain_override
            context = {
                'email': user.email,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                'platform_name': microsite.get_value('platform_name', settings.PLATFORM_NAME)
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = subject.replace('\n', '')
            email = loader.render_to_string(email_template_name, context)
            send_mail(subject, email, from_email, [user.email])


class TrueField(forms.BooleanField):
    """
    A boolean field that only accepts "true" (case-insensitive) as true
    """
    def to_python(self, value):
        # CheckboxInput converts string to bool by case-insensitive match to "true" or "false"
        if value is True:
            return value
        else:
            return None


_USERNAME_TOO_SHORT_MSG = _("Username must be minimum of two characters long")
_EMAIL_INVALID_MSG = _("A properly formatted e-mail is required")
_PASSWORD_INVALID_MSG = _("A valid password is required")
_NAME_TOO_SHORT_MSG = _("Your legal name must be a minimum of two characters long")


class AccountCreationForm(forms.Form):
    """
    A form to for account creation data. It is currently only used for
    validation, not rendering.
    """
    # TODO: Resolve repetition
    username = forms.SlugField(
        min_length=2,
        max_length=30,
        error_messages={
            "required": _USERNAME_TOO_SHORT_MSG,
            "invalid": _("Username should only consist of A-Z and 0-9, with no spaces."),
            "min_length": _USERNAME_TOO_SHORT_MSG,
            "max_length": _("Username cannot be more than %(limit_value)s characters long"),
        }
    )
    email = forms.EmailField(
        max_length=75,  # Limit per RFCs is 254, but User's email field in django 1.4 only takes 75
        error_messages={
            "required": _EMAIL_INVALID_MSG,
            "invalid": _EMAIL_INVALID_MSG,
            "max_length": _("Email cannot be more than %(limit_value)s characters long"),
        }
    )
    password = forms.CharField(
        min_length=2,
        error_messages={
            "required": _PASSWORD_INVALID_MSG,
            "min_length": _PASSWORD_INVALID_MSG,
        }
    )
    name = forms.CharField(
        min_length=2,
        error_messages={
            "required": _NAME_TOO_SHORT_MSG,
            "min_length": _NAME_TOO_SHORT_MSG,
        }
    )

    def __init__(
            self,
            data=None,
            extra_fields=None,
            extended_profile_fields=None,
            enforce_username_neq_password=False,
            enforce_password_policy=False,
            tos_required=True
    ):
        super(AccountCreationForm, self).__init__(data)
        extra_fields = extra_fields or {}
        self.extended_profile_fields = extended_profile_fields or {}
        self.enforce_username_neq_password = enforce_username_neq_password
        self.enforce_password_policy = enforce_password_policy
        if tos_required:
            self.fields["terms_of_service"] = TrueField(
                error_messages={"required": _("You must accept the terms of service.")}
            )

        # TODO: These messages don't say anything about minimum length
        error_message_dict = {
            "level_of_education": _("A level of education is required"),
            "gender": _("Your gender is required"),
            "year_of_birth": _("Your year of birth is required"),
            "mailing_address": _("Your mailing address is required"),
            "goals": _("A description of your goals is required"),
            "city": _("A city is required"),
            "country": _("A country is required"),
            #IITBombayX Added pincode Validation Start
            "pincode": _("A pincode is required")
            #IITBombayX End
        }
        for field_name, field_value in extra_fields.items():
            if field_name not in self.fields:
                if field_name == "honor_code":
                    if field_value == "required":
                        self.fields[field_name] = TrueField(
                            error_messages={
                                "required": _("To enroll, you must follow the honor code.")
                            }
                        )
                else:
                    required = field_value == "required"
		#IITBombayX : Registration field validation
                    min_length = 1 if field_name in ("gender", "level_of_education","state") else 2
                    error_message = error_message_dict.get(
                        field_name,
                        _("You are missing one or more required fields")
                    )
                    self.fields[field_name] = forms.CharField(
                        required=required,
                        min_length=min_length,
                        error_messages={
                            "required": error_message,
                            "min_length": error_message,
                        }
                    )

        for field in self.extended_profile_fields:
            if field not in self.fields:
                self.fields[field] = forms.CharField(required=False)

    def clean_password(self):
        """Enforce password policies (if applicable)"""
        password = self.cleaned_data["password"]
        if (
                self.enforce_username_neq_password and
                "username" in self.cleaned_data and
                self.cleaned_data["username"] == password
        ):
            raise ValidationError(_("Username and password fields cannot match"))
        if self.enforce_password_policy:
            try:
                validate_password_length(password)
                validate_password_complexity(password)
                validate_password_dictionary(password)
            except ValidationError, err:
                raise ValidationError(_("Password: ") + "; ".join(err.messages))
        return password

    def clean_year_of_birth(self):
        """
        Parse year_of_birth to an integer, but just use None instead of raising
        an error if it is malformed
        """
        try:
            year_str = self.cleaned_data["year_of_birth"]
            return int(year_str) if year_str is not None else None
        except ValueError:
            return None

    @property
    def cleaned_extended_profile(self):
        """
        Return a dictionary containing the extended_profile_fields and values
        """
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if key in self.extended_profile_fields and value is not None
        }
# IITBombayX Added Function for Pincode Validation Start
    def clean_pincode(self):
        pincode=self.cleaned_data['pincode']
        try:
          validate_integer(pincode)
        except:
          raise ValidationError(_("Pincode must be integer"))
        if pincode[0]=='0' or pincode[:2]=='10':
            raise ValidationError(_("Invalid Pincode valid pincode is required"))
        return pincode


#IITBombayX Added Function for Aadhar Validation Start
    
    def clean_aadhar_id(self):
        aadhar_id=self.cleaned_data['aadhar_id']
        if aadhar_id:
            try:
               validate_integer(aadhar_id)
            except:
               raise ValidationError(_("Aadhar ID must be an integer of at least 12 digits."))
        if aadhar_id and len(aadhar_id)<12:
               raise ValidationError(_("Aadhar ID must be an integer of at least 12 digits."))
        return aadhar_id

#IITBombayX Added Function for City Validation Start

    def clean_city(self):
        city=self.cleaned_data['city']
        if not re.match('^[a-zA-Z0-9]+[ ,a-zA-Z0-9]*[a-zA-Z]+$',city) or city.isdigit():
           raise ValidationError('%s is not a valid format for city' % city)
        return city
 


#IITBombayX End

#IITBombayX form models for Adding and Editing Team Members Profile
class TeamForm(forms.Form):
         def alpha(value):
            content="".join(value.split())
            if not re.match('^[a-zA-Z.]*$',content):
              raise ValidationError('%s is not a valid name' % value)
         def alphanumeric(value):
            content="".join(value.split())
            if not re.match('^[0-9a-zA-Z.@]*$',content):
              raise ValidationError('%s is not a valid format for biodata' % value)
         def t_valid(value):
            content="".join(value.split())
            if not re.match('^[a-zA-Z.,]*$',content):
              raise ValidationError('%s is not a valid name' % value)

         name=forms.CharField(widget=forms.TextInput , max_length=64, required=False, label="Name",validators=[alpha])
         team_name=forms.CharField(widget=forms.TextInput , max_length=64, required=False, label="Team Name",validators=[t_valid])
         role=forms.CharField(widget=forms.TextInput , max_length=32,required=False, label="Role",validators=[alpha])
         biodata=forms.CharField(widget=forms.Textarea , max_length=255,required=False, label="Brief Info")
         photo = forms.FileField(widget=forms.ClearableFileInput(attrs={"onchange":"upload_img(this);"}), required=False, label="Picture")
        # photo= AdvancedFileInput()


         def clean(self):
             cleaned_data = super(TeamForm, self).clean()
             photo_data = cleaned_data.get("photo")
             name_data= cleaned_data.get("name")
             tname_data= cleaned_data.get("team_name")
             bio_data= cleaned_data.get("biodata")
             role_data=cleaned_data.get("role")

             ext = [".jpg",".jpeg",".gif"]
             if not name_data:
                raise forms.ValidationError("Name is required")
             if not tname_data:
                 raise forms.ValidationError("Team Name is required")
             if not role_data:
                  raise forms.ValidationError("Role is required")
             if not bio_data:
                  raise forms.ValidationError("Info is required")
             if photo_data:
                if not photo_data.name.endswith(tuple(ext)):
                     raise forms.ValidationError("Only jpg jpeg gif files are allowed!")
             return cleaned_data
                                                                                                           

class EditTeamForm(forms.Form):
         
         def __init__(self, *args, **kwargs):
               self.name = kwargs.pop('name', None)
               self.role = kwargs.pop('role', None)
               self.team = kwargs.pop('team', None)
               self.biodata=kwargs.pop('biodata',None)
               
               super(EditTeamForm, self).__init__(*args, **kwargs)
               def alpha(value):
                  content="".join(value.split())
                  if not re.match('^[a-zA-Z.]*$',content):
                        raise ValidationError('%s is not a valid name' % value)
               def alphanumeric(value):
                  content="".join(value.split())
                  if not re.match('^[0-9a-zA-Z.@]*$',content):
                    raise ValidationError('%s is not a valid format for biodata' % value)
               def t_valid(value):
                  content="".join(value.split())
                  if not re.match('^[a-zA-Z.,]*$',content):
                    raise ValidationError('%s is not a valid name' % value)


               self.fields['name'] = forms.CharField(required=False, widget=forms.TextInput, initial=self.name, label="Name:",max_length=64,validators=[alpha])
               self.fields['tname'] = forms.CharField(required=False, widget=forms.TextInput,initial=self.team, label="Team Name:",max_length=64,validators=[t_valid])
               self.fields['role'] = forms.CharField(required=False, widget=forms.TextInput,  initial=self.role, label="Role:",max_length=32,validators=[alpha])
               self.fields['biodata'] = forms.CharField(required=False, widget=forms.Textarea, initial=self.biodata, label="Brief Info:",max_length=255)

               self.fields['photo'] = forms.FileField(widget=forms.ClearableFileInput, required=False, label="Picture")


         def clean(self):
             cleaned_data = super(EditTeamForm, self).clean()
             photo_data = cleaned_data.get("photo")
             name_data= cleaned_data.get("name")
             tname_data= cleaned_data.get("tname")
             bio_data= cleaned_data.get("biodata")
             role_data=cleaned_data.get("role")

             ext = [".jpg",".jpeg",".gif"]
             if not name_data:
                raise forms.ValidationError("Name is required")
             if not tname_data:
                 raise forms.ValidationError("Team Name is required")
             if not role_data:
                  raise forms.ValidationError("Role is required")
             if not bio_data:
                  raise forms.ValidationError("Info is required")
             if photo_data:
                if not photo_data.name.endswith(tuple(ext)):
                     raise forms.ValidationError("Only jpg jpeg gif files are allowed!")
             return cleaned_data


#IITBombayX form model  for Adding and Editing Team Members Profile ends




