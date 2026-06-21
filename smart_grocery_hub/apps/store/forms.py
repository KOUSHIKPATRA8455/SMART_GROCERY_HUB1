from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        widget=forms.Select(
            choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)],
            attrs={"class": "form-select"},
        ),
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Share your experience (optional)"}),
        }
