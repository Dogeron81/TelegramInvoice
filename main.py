import os
import telebot
import dotenv
import jinja2
import pdfkit
from datetime import datetime, timedelta
import base64
import threading

dotenv.load_dotenv()
API_KEY = os.getenv('API_KEY')

def main():

    bot = telebot.TeleBot(API_KEY)
    @bot.message_handler(commands=['Greet'])
    def greet(message):
        bot.reply_to(message, "Hello! How can I assist you today?")

    @bot.message_handler(commands=['invoice'])
    def handle_invoice(message):
        chat_id = message.chat.id
        try:
            content = message.text[len('/invoice'):].strip()
            parts = [part.strip() for part in content.split(',')]
            if len(parts) != 3:
                bot.reply_to(message, "Please use the format:\n/invoice Name, $Amount, Description")
                return
            name, amount, description = parts
            amount = '$' + amount

            invoice_date, due_date, invoice_number = get_invoice_details()
            create_invoice(name, invoice_number, invoice_date, due_date, description, amount)

            with open(f'saved_invoices/{invoice_number}.pdf', 'rb') as invoice_file:
                bot.send_document(chat_id, invoice_file, caption=f"Invoice for {name} - {description}")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error processing invoice: {str(e)}")

    def run_bot():
        bot.polling(none_stop=True)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    try:
        while True:
            if input().strip().lower() == 'q':
                print("Stopping bot...")
                bot.stop_polling()  # Gracefully stop polling
                break
    except KeyboardInterrupt:
        print("Interrupted by user")
        bot.stop_polling()

def get_invoice_details():
    today = datetime.now().strftime('%Y%m%d')
    invoice_number = f"INV-{today}-{os.urandom(4).hex().upper()}"

    invoice_date = datetime.today().strftime("%d-%m-%Y")
    due_date = (datetime.today() + timedelta(days=7)).strftime("%d-%m-%Y")

    return invoice_date, due_date, invoice_number

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
    output_file = os.path.join(output_dir, f'{invoice_number}.pdf')

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)
    template = template = template_env.get_template('page.html')
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {'enable-local-file-access': ''}
    pdfkit.from_string(output_text, output_file, configuration=config, options=options)



if __name__ == "__main__":
    main()