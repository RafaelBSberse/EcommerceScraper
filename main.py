import os, schedule, time, argparse, dotenv

dotenv.load_dotenv()

parser = argparse.ArgumentParser(description="Web Scraper que notifica cada anuncio novo de um determinado item no Mercado Livre")

parser.add_argument('-i', '--interval', type=int, help='Intervalo de tempo entre a execução do scraper', default=600)
parser.add_argument('-l', '--link', type=str, help='Link da listagem do anuncio no Mercado Livre')
parser.add_argument('-s', '--search', type=str, help='Nome do produto')
parser.add_argument('-a', '--amount', type=float, help='Valor máximo do produto para receber notificação', default=0)

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
SENHA = os.getenv("SENHA")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO")

ARGS = parser.parse_args()

def gera_url():
    return "https://lista.mercadolivre.com.br/" + "-".join([word.lower() for word in filter(None, ARGS.search.split())])


def main():
    if not ARGS.link and not ARGS.search:
        print("Você precisa especificar um link através do argumento ('-l' ou '--link') ou uma pesquisa através do argumento ('-s', '--search')")
        exit()

    page = ARGS.link if ARGS.link else gera_url()

    print('Schedule inicializado')
    schedule.every(ARGS.interval).seconds.do(lambda: os.system('scrapy crawl product_search -a page=' + page + " -a max_amount=" + str(ARGS.amount)))
    print('Proximo Crawl em: ' + str(schedule.next_run()))

    while True:
        schedule.run_pending()
        time.sleep(1)

def validate():
    if not EMAIL_SENDER or not SENHA:
        print("Você precisa definir um email para fazer o envio das notificações.")
        exit()

    if not EMAIL_DESTINATARIO:
        print("Você precisa definir um email para receber as notificações.")
        exit()

if __name__ == "__main__":
    validate()
    main()
    