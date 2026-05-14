#dashboard/forms.py

from django import forms
from organizations.models import OrganizationMailConfig


class OrganizationMailConfigForm(forms.ModelForm):
    class Meta:
        model = OrganizationMailConfig
        fields = [
            "smtp_host",
            "port",
            "username",
            "password",
            "use_tls",
            "use_ssl",
            "from_email",
        ]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

    def clean(self):
        cleaned = super().clean()

        smtp_host = cleaned.get("smtp_host")
        use_tls = cleaned.get("use_tls")
        use_ssl = cleaned.get("use_ssl")
        password = cleaned.get("password")

        # ❌ TLS + SSL not allowed together
        if use_tls and use_ssl:
            raise forms.ValidationError(
                "Enable either TLS or SSL, not both."
            )

        if smtp_host:
            if not cleaned.get("port"):
                self.add_error("port", "Required when SMTP is configured.")
            if not cleaned.get("username"):
                self.add_error("username", "Required when SMTP is configured.")

            # 🔥 password required ONLY if not already saved
            if not password and not self.instance.pk:
                self.add_error(
                    "password",
                    "Password required for new SMTP config."
                )

        return cleaned

