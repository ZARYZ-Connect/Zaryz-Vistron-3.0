from django import forms


class ContactForm(forms.Form):
    full_name = forms.CharField(max_length=255, min_length=2)
    email     = forms.EmailField()
    phone     = forms.CharField(max_length=50, required=False)
    company   = forms.CharField(max_length=255, required=False)
    subject   = forms.CharField(max_length=255, required=False)
    message   = forms.CharField(
                    widget=forms.Textarea,
                    min_length=10,
                    max_length=5000
                )
    website   = forms.CharField(required=False,
                    widget=forms.HiddenInput)  # honeypot

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError("Bot detected.")
        return ''
