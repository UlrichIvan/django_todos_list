import re
from django.forms import ModelForm

from .models import Todo, UserTodo, FactorAuth


class TodoForm(ModelForm):
    class Meta:
        model = Todo
        exclude = ["created_at", "updated_at", "deleted_at", "done", "user_id"]


class EditTodoForm(ModelForm):
    class Meta:
        model = Todo
        fields = ["title", "content", "done"]


class UserForm(ModelForm):

    class Meta:
        model = UserTodo
        fields = ["first_name", "last_name", "email", "password"]

    rgx_password = r"^[a-zA-Z0-9]{12}$"

    def is_valid(self):
        if re.match(self.rgx_password, self.data["password"]) == None:
            self.add_error(
                "password", "password must be content 12 alphanumics characters"
            )
            super().is_valid()
            return False
        if self.data["password"] != self.data["confirm_password"]:
            self.add_error("password", "password and confirm password must be the same")
            super().is_valid()
            return False
        return super().is_valid()


class UserNewPasswordForm(ModelForm):

    class Meta:
        model = UserTodo
        fields = ["code", "password"]

    rgx_password = r"^[a-zA-Z0-9]{12}$"
    rgx_code = r"^[a-zA-Z0-9]{7,10}$"

    def is_valid(self):
        if re.match(self.rgx_password, self.data["password"]) == None:
            self.add_error(
                "password", "password must be content 12 alphanumics characters"
            )
            return False
        if self.data["password"] != self.data["confirm_password"]:
            self.add_error("password", "password and confirm password must be the same")
            return False

        if re.match(self.rgx_code, self.data["code"]) == None:
            self.add_error("code", "code invalid or expired")
            return False
        setattr(
            self,
            "cleaned_data",
            dict(code=self.data.get("code"), password=self.data.get("password")),
        )
        return True


class UserActivationForm(ModelForm):

    class Meta:
        model = UserTodo
        fields = ["code"]

    rgx_code = r"^[a-zA-Z0-9]{7,10}$"

    def is_valid(self):

        if re.match(self.rgx_code, self.data["code"]) == None:
            return False
        else:
            setattr(self, "cleaned_data", dict(code=self.data["code"]))
            return True


class UserFactAuthForm(ModelForm):

    class Meta:
        model = FactorAuth
        fields = ["code"]

    rgx_code = r"^[a-zA-Z0-9]{7,10}$"

    def is_valid(self):

        if re.match(self.rgx_code, self.data["code"]) == None:
            return False
        else:
            setattr(self, "cleaned_data", dict(code=self.data["code"]))
            return True


class UserNewCodeForm(ModelForm):

    class Meta:
        model = UserTodo
        fields = ["email"]

    rgx_email = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

    def is_valid(self):
        if re.match(self.rgx_email, self.data["email"]) == None:
            return False
        else:
            setattr(self, "cleaned_data", dict(email=self.data["email"]))
            return True


class UserLoginForm(ModelForm):

    class Meta:
        model = UserTodo
        fields = ["email", "password"]

    rgx_email = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

    rgx_password = r"^[a-zA-Z0-9]{12}$"

    def is_valid(self):
        if re.match(self.rgx_email, self.data["email"]) == None:
            return False
        elif re.match(self.rgx_password, self.data["password"]) == None:
            return False
        else:
            setattr(
                self,
                "cleaned_data",
                dict(email=self.data["email"], password=self.data["password"]),
            )
            return True
