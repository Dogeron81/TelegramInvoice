import jinja2
import pdfkit
from datetime import datetime, timedelta
import base64
import os


client_name = "John Doe"
invoice_number = "123465775"
invoice_date = datetime.today().strftime("%d-%m-%Y")    
due_date = (datetime.today() + timedelta(days=7)).strftime("%d-%m-%Y")
service = "Web Development"
price = "1500.00"

def create_invoice(client_name, invoice_number, invoice_date, due_date, service, price):

    with open("graphics/dogeronLogo.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    context = {
        'client_name': client_name,
        'invoice_number': invoice_number,
        'invoice_date': invoice_date,
        'due_date': due_date,
        'service': service,
        'price': price
    }
    image_data_url = f"data:image/png;base64,{encoded_string}"
    context['logo'] = image_data_url

    output_dir = 'saved_invoices'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'invoice_{invoice_number}.pdf')

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)
    template = template = template_env.get_template('page.html')
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {'enable-local-file-access': ''}
    pdfkit.from_string(output_text, output_file, configuration=config, options=options)

create_invoice(client_name, invoice_number, invoice_date, due_date, service, price)