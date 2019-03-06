import pytest

from common.tests.conftest import *  # noqa
from notifications.enums import NotificationType
from notifications.models import NotificationTemplate


@pytest.fixture
def notification_template_event_created(settings):
    settings.LANGUAGES = (('fi', 'Finnish'), ('en', 'English'))

    template = NotificationTemplate.objects.language('en').create(
        type=NotificationType.EVENT_CREATED,
        subject="test subject, variable value: {{ subject_var }}!",
        body_html="<b>test body HTML</b>, variable value: {{ body_html_var }}!",
        body_text="test body text, variable value: {{ body_text_var }}!",

    )
    template.set_current_language('fi')
    template.subject = "testiotsikko, muuttujan arvo: {{ subject_var }}!"
    template.body_html = "<b>testihötömölöruumis</b>, muuttujan arvo: {{ body_html_var }}!"
    template.body_text = "testitekstiruumis, muuttujan arvo: {{ body_text_var }}!"

    template.save()

    return template
