from airflow.utils.email import send_email
from airflow.models import Variable

def notify_email(context):
    """Send email notification on task failure."""
    subject = f"Airflow Alert: {context['task_instance'].dag_id} Failed"
    html_content = f"""
    <p>Task: {context['task_instance'].task_id} in DAG: {context['task_instance'].task_id} has failed.</p>
    <p>Execution Date: {context['execution_date']}</p>
    <p>Log URL: {context['task_instance'].log_url}</p>
    <p>Start Date: {context['task_instance'].start_date}</p>
    <p>End Date: {context['task_instance'].end_date}</p>
    <p>Duration: {context['task_instance'].duration} seconds</p>
    """
    emails = Variable.get('default_email_recipients')
    emails = emails.split(',')
    send_email(to=emails, subject=subject, html_content=html_content)

def success_email(context):
    """Send email notification on task success."""
    subject = f"Airflow Notification: {context['task_instance'].dag_id} Succeeded"
    html_content = f"""
    <p>Task: {context['task_instance'].task_id} in DAG: {context['task_instance'].task_id} has succeeded.</p>
    <p>Execution Date: {context['execution_date']}</p>
    <p>Log URL: {context['task_instance'].log_url}</p>
    <p>Start Date: {context['task_instance'].start_date}</p>
    <p>End Date: {context['task_instance'].end_date}</p>
    <p>Duration: {context['task_instance'].duration} seconds</p>
    """
    emails = Variable.get('default_email_recipients')
    emails = emails.split(',')
    send_email(to=emails, subject=subject, html_content=html_content)
