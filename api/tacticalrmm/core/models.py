from loguru import logger
import pytz
import time
import smtplib
from email.message import EmailMessage
from twilio.rest import Client as TwClient

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from logs.models import BaseAuditModel

logger.configure(**settings.LOG_CONFIG)

TZ_CHOICES = [(_, _) for _ in pytz.all_timezones]


class CoreSettings(BaseAuditModel):
    email_alert_recipients = ArrayField(
        models.EmailField(null=True, blank=True),
        null=True,
        blank=True,
        default=list,
    )
    sms_alert_recipients = ArrayField(
        models.CharField(max_length=255, null=True, blank=True),
        null=True,
        blank=True,
        default=list,
    )
    twilio_number = models.CharField(max_length=255, null=True, blank=True)
    twilio_account_sid = models.CharField(max_length=255, null=True, blank=True)
    twilio_auth_token = models.CharField(max_length=255, null=True, blank=True)
    smtp_from_email = models.CharField(
        max_length=255, null=True, blank=True, default="from@example.com"
    )
    smtp_host = models.CharField(
        max_length=255, null=True, blank=True, default="smtp.gmail.com"
    )
    smtp_host_user = models.CharField(
        max_length=255, null=True, blank=True, default="admin@example.com"
    )
    smtp_host_password = models.CharField(
        max_length=255, null=True, blank=True, default="changeme"
    )
    smtp_port = models.PositiveIntegerField(default=587, null=True, blank=True)
    smtp_requires_auth = models.BooleanField(default=True)
    default_time_zone = models.CharField(
        max_length=255, choices=TZ_CHOICES, default="America/Los_Angeles"
    )
    mesh_token = models.CharField(max_length=255, null=True, blank=True, default="")
    mesh_username = models.CharField(max_length=255, null=True, blank=True, default="")
    mesh_site = models.CharField(max_length=255, null=True, blank=True, default="")
    agent_auto_update = models.BooleanField(default=True)
    workstation_policy = models.ForeignKey(
        "automation.Policy",
        related_name="default_workstation_policy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    server_policy = models.ForeignKey(
        "automation.Policy",
        related_name="default_server_policy",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def save(self, *args, **kwargs):
        if not self.pk and CoreSettings.objects.exists():
            raise ValidationError("There can only be one CoreSettings instance")

        # for install script
        if not self.pk:
            try:
                self.mesh_site = settings.MESH_SITE
                self.mesh_username = settings.MESH_USERNAME
                self.mesh_token = settings.MESH_TOKEN_KEY
            except:
                pass

        return super(CoreSettings, self).save(*args, **kwargs)

    def __str__(self):
        return "Global Site Settings"

    @property
    def sms_is_configured(self):
        return all(
            [
                self.sms_alert_recipients,
                self.twilio_auth_token,
                self.twilio_account_sid,
                self.twilio_number,
            ]
        )

    @property
    def email_is_configured(self):
        # smtp with username/password authentication
        if (
            self.smtp_requires_auth
            and self.email_alert_recipients
            and self.smtp_from_email
            and self.smtp_host
            and self.smtp_host_user
            and self.smtp_host_password
            and self.smtp_port
        ):
            return True
        # smtp relay
        elif (
            not self.smtp_requires_auth
            and self.email_alert_recipients
            and self.smtp_from_email
            and self.smtp_host
            and self.smtp_port
        ):
            return True

        return False

    def send_mail(self, subject, body, test=False):

        if not self.email_is_configured:
            if test:
                return "Missing required fields (need at least 1 recipient)"
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.smtp_from_email
            msg["To"] = ", ".join(self.email_alert_recipients)
            msg.set_content(body)

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
                if self.smtp_requires_auth:
                    server.ehlo()
                    server.starttls()
                    server.login(self.smtp_host_user, self.smtp_host_password)
                    server.send_message(msg)
                    server.quit()
                else:
                    # smtp relay. no auth required
                    server.send_message(msg)
                    server.quit()

        except Exception as e:
            logger.error(f"Sending email failed with error: {e}")
            if test:
                return str(e)
        else:
            return True

    def send_sms(self, body):
        if not self.sms_is_configured:
            return

        tw_client = TwClient(self.twilio_account_sid, self.twilio_auth_token)
        for num in self.sms_alert_recipients:
            try:
                tw_client.messages.create(body=body, to=num, from_=self.twilio_number)
            except Exception as e:
                logger.error(f"SMS failed to send: {e}")

    @staticmethod
    def serialize(core):
        # serializes the core and returns json
        from .serializers import CoreSerializer

        return CoreSerializer(core).data
