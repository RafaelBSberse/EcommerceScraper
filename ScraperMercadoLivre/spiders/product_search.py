import scrapy, json, re, smtplib, os

from email.message import EmailMessage

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
SENHA = os.getenv("SENHA")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")

class ProductSearchSpider(scrapy.Spider):
    name = "product_search"

    new_itens = dict()
    itens_to_send = list()

    def start_requests(self):
        self.new_itens = {}
        self.itens_to_send = []
        yield scrapy.Request(self.page)

    def send_email(self):
        msg = EmailMessage()
        msg["Subject"] = "Novos anuncios para seu produto"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_DESTINATARIO

        content = str()

        for item in self.itens_to_send:
            content += ("Titulo do anuncio: %(title)s\nPreço do anuncio: R$ %(amount)s\nLink: %(href)s\n\n" % item)

        msg.set_content(content)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, SENHA)
            smtp.send_message(msg)


    def parse(self, response):
        itens_persistence = open("itens.json", "r+", encoding="utf8")
        read = itens_persistence.read()
        itens = json.loads(read if read else "{}")

        products = response.css("li.ui-search-layout__item")

        self.max_amount = float(self.max_amount)
        max_amount = self.max_amount if self.max_amount != 0 else float('inf')

        for product in products:
            href = product.css('a.ui-search-link::attr(href)').get()
            amount = product.css('span.andes-money-amount__fraction::text').get()
            title = product.css('h2.ui-search-item__title::text').get()
            match = re.search(r"MLB-?\d+", href)
            codigo = match.group() if match else None

            if float(amount.replace(".", "").replace(",", ".")) < max_amount:
                new_item = { 
                    "title": title,
                    "amount": amount,
                    "href": href
                }

                if codigo not in itens:
                    self.itens_to_send.append(new_item)

                self.new_itens[codigo] = new_item
        
        next_page = response.xpath("//a[contains(@title, 'Seguinte')]/@href").get()

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
        else:
            if len(self.itens_to_send) > 0:
                self.send_email()

            json_object = json.dumps(self.new_itens, indent=3, ensure_ascii=False)
            itens_persistence.seek(0)
            itens_persistence.write(json_object)
            itens_persistence.truncate()
            itens_persistence.close()

