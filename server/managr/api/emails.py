import os
import uuid
from io import StringIO
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.mail import get_connection
from django.template.loader import render_to_string
from django.core.mail import get_connection
from email.mime.application import MIMEApplication
import base64
from email.mime.text import MIMEText


def create_gmail_message(sender, sent_to, subject, template, name, context={}, cc=[], bcc=[]):
    html_body = render_to_string(template, context)
    message = MIMEText(html_body, "html")
    message["to"] = sent_to
    message["from"] = f"{name} <{sender}>"
    message["subject"] = subject
    if cc:
        message["cc"] = ", ".join(cc)
    if bcc:
        message["bcc"] = ", ".join(bcc)
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {"raw": raw}


def create_ms_message(sender, sent_to, subject, template, name, context={}, cc=[], bcc=[]):
    html_body = render_to_string(template, context)
    email_message = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "from": {"emailAddress": {"address": sender, "name": name}},
            "toRecipients": [{"emailAddress": {"address": sent_to}}],
        }
    }
    if len(cc):
        email_message["message"]["ccRecipients"] = [
            {"emailAddress": {"address": address}} for address in cc
        ]
    if len(bcc):
        email_message["message"]["bccRecipients"] = [
            {"emailAddress": {"address": address}} for address in bcc
        ]
    return email_message


def send_html_email(
    subject,
    template,
    send_from,
    send_to,
    context={},
    bcc_emails=[],
    files=[],
    headers={},
    cc_emails=[],
    user=False,
):
    """Generic sender to build and send an HTML email with a plain-text fallback.

    Args:
        subject (str): Subject of the email.
        template (str): Path to the HTML template to use for this email. Use the Django
            template loader path.
        send_from (str): The email address of the sender.
        send_to (str or list of str): Email address(es) of recipients.
        context (dict, optional): Dictionary of context variables needed to render
            the HTML template. Defaults to an empty :obj:`dict`.
        bcc_emails (list of str, optional): List of email addresses to BCC
            on the email. Defaults to an empty :obj:`list`.
        files (list of str or tuple of (str, StringIO.OutputType), optional): Files to
            attach to the email. For flexibility, filenames or tuples of
            (filename, StringIO.OuputType)  are accepted. Defaults to empty `list`.

    Returns: None
    """
    assert isinstance(
        send_to, (list, tuple, str)
    ), "send_to must be an instance of list, tuple, or str"

    if isinstance(send_to, str):
        send_to = [send_to]

    # Email subject *must not* contain newlines
    subject = "".join(subject.splitlines())

    # Render HTML and use premailer transform to force inline CSS
    html_body = render_to_string(template, context)

    # TODO: Generate plaintext version of the HTML email
    plaintext_body = (
        "This is an HTML email. If you can read this, then "
        "your email client does not support HTML emails. "
        "Please contact us at {0} to report the problem.".format(settings.SERVER_EMAIL)
    )
    # END TODO

    email = EmailMultiAlternatives(
        subject, plaintext_body, send_from, send_to, bcc_emails, headers=headers, cc=cc_emails
    )
    email.attach_alternative(html_body, "text/html")

    # Handle file attachments
    for f in files or []:
        if isinstance(f, tuple):
            # Attach in-memory files with filename
            if isinstance(f[1], StringIO.OutputType):
                part = MIMEApplication(f[1].getvalue(), Name=f[0])
                part["Content-Disposition"] = 'attachment; filename="%s"' % f[0]
            else:
                # No other file type support -- only StringIO
                continue
        elif isinstance(f, str):
            # Read file and create attachment
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=os.path.basename(f))
                part["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(f)
        else:
            # Ignore list elements that are neither a tuple or string
            continue
        email.attach(part)
    try:
        if user:
            organiation = user.organization
            if organiation.smtp_user is not None:
                smtp_user = user.organization.smtp_user
                smtp_pass = user.organization.smtp_pass
                smtp_host = settings.EMAIL_HOST
                smtp_port = settings.EMAIL_PORT

                # Override the Django email backend settings
                connection = get_connection(
                    backend="django.core.mail.backends.smtp.EmailBackend",
                    host=smtp_host,
                    port=smtp_port,
                    username=smtp_user,
                    password=smtp_pass,
                    use_tls=True,
                )
                email.connection = connection
        print(email)
        email.send(fail_silently=False)
    except Exception as e:
        print(str(e))


def send_test_email(email_from, email_to):
    send_html_email(
        "This is Test",
        "core/email-templates/developer-test.html",
        email_from,
        [email_to],
    )


def send_mailgun_email(user, name, subject, recipient, body, bcc=[], cc=[], draft_id=None):
    from managr.comms.models import EmailTracker
    from managr.comms.serializers import EmailTrackerSerializer

    context = {"body": body}
    message_id = f"{uuid.uuid4()}-{user.email}"
    res = {"sent": False}
    try:
        send_html_email(
            subject,
            "core/email-templates/user-email.html",
            f"{user.full_name} <{user.email}>",
            [recipient],
            context=context,
            bcc_emails=bcc,
            cc_emails=cc,
            headers={
                "Reply-To": f"{user.full_name} <{user.first_name}.{user.last_name}@mg.managr.ai>",
                "X-Managr-Id": message_id,
                "Message-ID": message_id,
            },
            user=user,
        )
        user.add_meta_data("emailSent")
        if draft_id:
            instance = EmailTracker.objects.get(id=draft_id)
        else:
            serializer = EmailTrackerSerializer(
                data={
                    "user": user.id,
                    "recipient": recipient,
                    "body": body,
                    "subject": subject,
                    "message_id": message_id,
                    "name": name,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instance = serializer.instance
        instance.add_activity("sent")
        res["sent"] = True
        return res
    except Exception as e:
        res["error"] = str(e)
        return res
