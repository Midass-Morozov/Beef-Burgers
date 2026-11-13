from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from menu.models import Category, Product
import urllib.request


CATEGORIES = [
    ('Бургеры', 'burgers'),
    ('Картофель и снеки', 'fries'),
    ('Напитки', 'drinks'),
]

PRODUCTS = [
    ('burgers', 'Чизбургер', 'Говяжья котлета, сыр чеддер, соленый огурец, лук, горчица, кетчуп', 120, True,
     'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600'),
    ('burgers', 'Биг Мак', 'Две котлеты, тройная булочка, салат, сыр, огурцы, фирменный соус', 250, True,
     'https://images.unsplash.com/photo-1550547660-d9450f859349?w=600'),
    ('burgers', 'Гамбургер', 'Говяжья котлета, соленый огурец, лук, горчица, кетчуп', 90, False,
     'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=600'),
    ('burgers', 'Двойной чизбургер', 'Две котлеты, двойной сыр, огурец, лук, горчица, кетчуп', 180, True,
     'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=600'),
    ('burgers', 'Чикен Бургер', 'Куриная котлета, салат, майонез', 150, False,
     'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=600'),
    ('burgers', 'Филе-о-Фиш', 'Рыбная котлета, сыр, соус тартар', 190, False,
     'https://images.unsplash.com/photo-1550317138-10000687a72b?w=600'),
    ('fries', 'Картофель фри', 'Хрустящий картофель фри, средняя порция', 80, True,
     'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600'),
    ('fries', 'Картофель по-деревенски', 'Картофельные дольки с пряностями', 100, False,
     'https://images.unsplash.com/photo-1518013431117-eb1465fa5752?w=600'),
    ('fries', 'Наггетсы 6 шт', 'Куриные наггетсы, 6 штук', 130, True,
     'https://images.unsplash.com/photo-1562967914-608f82629710?w=600'),
    ('drinks', 'Кока-Кола 0.5', 'Классическая Coca-Cola, 0.5 л', 60, True,
     'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=600'),
    ('drinks', 'Спрайт 0.5', 'Освежающий Sprite, 0.5 л', 60, False,
     'https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=600'),
    ('drinks', 'Молочный коктейль', 'Коктейль ванильный, 0.4 л', 120, True,
     'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=600'),
]


class Command(BaseCommand):
    help = "Заполняет базу категориями и блюдами McDonald's"

    def handle(self, *args, **options):
        for name, slug in CATEGORIES:
            cat, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            if created:
                self.stdout.write(self.style.SUCCESS(f'OK категория: {name}'))

        for slug, name, desc, price, hit, img_url in PRODUCTS:
            category = Category.objects.get(slug=slug)
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': desc,
                    'price': price,
                    'is_featured': hit,
                }
            )
            if created:
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=15) as response:
                        img_data = response.read()
                    filename = f'{slug}_{name.replace(" ", "_")[:20]}.jpg'
                    product.image.save(filename, ContentFile(img_data), save=True)
                    self.stdout.write(self.style.SUCCESS(f'OK {name} — {price} сом (с фото)'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'! {name} — без фото ({e})'))
            else:
                self.stdout.write(f'• уже есть: {name}')

        self.stdout.write(self.style.SUCCESS('\nГотово! Все блюда в базе.'))