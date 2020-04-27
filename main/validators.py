from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_vk_link(value):
    if not value.startswith("https://vk.com/"):
        raise ValidationError(
            _(
                "%(value)s должно быть ссылкой на страницу ВК и начинаться на "
                '"https://vk.com".'
            ),
            params={"value": value},
        )
