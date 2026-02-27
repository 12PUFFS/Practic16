"""
Система оформления заказа кофе в кофейне.
Используется паттерн Builder для пошагового создания заказа.
"""

from dataclasses import dataclass
from typing import Tuple, List, Set, Optional
from enum import Enum


class CoffeeBase(str, Enum):
    """Допустимые виды основы кофе"""
    ESPRESSO = "espresso"
    AMERICANO = "americano"
    LATTE = "latte"
    CAPPUCCINO = "cappuccino"


class CoffeeSize(str, Enum):
    """Допустимые размеры кофе"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class MilkType(str, Enum):
    """Допустимые типы молока"""
    NONE = "none"
    WHOLE = "whole"
    SKIM = "skim"
    OAT = "oat"
    SOY = "soy"


@dataclass(frozen=True)
class CoffeeOrder:
    """
    Неизменяемый объект заказа кофе.
    
    Поля:
        base: основа кофе
        size: размер
        milk: тип молока
        syrups: кортеж сиропов
        sugar: количество сахара (чайных ложек)
        iced: со льдом или нет
        price: итоговая цена
        description: человекочитаемое описание
    """
    base: str
    size: str
    milk: str = "none"
    syrups: Tuple[str, ...] = ()
    sugar: int = 0
    iced: bool = False
    price: float = 0.0
    description: str = ""
    
    def __str__(self) -> str:
        """Возвращает описание заказа или строку с ценой, если описание пусто."""
        if self.description:
            return self.description
        return f"{self.size} {self.base} - {self.price}₽"


class CoffeeOrderBuilder:
    """
    Fluent Builder для создания заказа кофе.
    
    Правила и ограничения:
    - Обязательные поля: base и size
    - Сахар: от 0 до 5 чайных ложек
    - Сиропы: максимум 4, дубликаты игнорируются
    - Цена рассчитывается на основе базы, размера, молока, сиропов и льда
    """
    
    
    BASE_PRICES = {
        "espresso": 200,
        "americano": 250,
        "latte": 300,
        "cappuccino": 320,
    }
    
    
    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4,
    }
    
    
    MILK_PRICES = {
        "none": 0,
        "whole": 30,
        "skim": 30,
        "oat": 60,
        "soy": 50,
    }
    
    
    SYRUP_PRICE = 40
    
    
    ICED_PRICE = 0.2
    
   
    MAX_SUGAR = 5
    MAX_SYRUPS = 4
    
    def __init__(self):
        """Инициализация билдера с значениями по умолчанию."""
        self.reset()
    
    def reset(self) -> 'CoffeeOrderBuilder':
        """Сброс билдера к начальному состоянию."""
        self._base: Optional[str] = None
        self._size: Optional[str] = None
        self._milk: str = "none"
        self._syrups: Set[str] = set()
        self._sugar: int = 0
        self._iced: bool = False
        return self
    
    def set_base(self, base: str) -> 'CoffeeOrderBuilder':
        """Устанавливает основу кофе."""
        if base not in [b.value for b in CoffeeBase]:
            raise ValueError(f"Недопустимая основа: {base}. Допустимо: {[b.value for b in CoffeeBase]}")
        self._base = base
        return self
    
    def set_size(self, size: str) -> 'CoffeeOrderBuilder':
        """Устанавливает размер кофе."""
        if size not in [s.value for s in CoffeeSize]:
            raise ValueError(f"Недопустимый размер: {size}. Допустимо: {[s.value for s in CoffeeSize]}")
        self._size = size
        return self
    
    def set_milk(self, milk: str) -> 'CoffeeOrderBuilder':
        """Устанавливает тип молока."""
        if milk not in [m.value for m in MilkType]:
            raise ValueError(f"Недопустимый тип молока: {milk}. Допустимо: {[m.value for m in MilkType]}")
        self._milk = milk
        return self
    
    def add_syrup(self, name: str) -> 'CoffeeOrderBuilder':
        """Добавляет сироп. Игнорирует дубликаты."""
        if len(self._syrups) >= self.MAX_SYRUPS:
            raise ValueError(f"Нельзя добавить больше {self.MAX_SYRUPS} сиропов")
        self._syrups.add(name.lower())
        return self
    
    def set_sugar(self, teaspoons: int) -> 'CoffeeOrderBuilder':
        """Устанавливает количество сахара (0-5 чайных ложек)."""
        if not 0 <= teaspoons <= self.MAX_SUGAR:
            raise ValueError(f"Сахар должен быть от 0 до {self.MAX_SUGAR} чайных ложек")
        self._sugar = teaspoons
        return self
    
    def set_iced(self, iced: bool = True) -> 'CoffeeOrderBuilder':
        """Устанавливает, будет ли кофе со льдом."""
        self._iced = iced
        return self
    
    def clear_extras(self) -> 'CoffeeOrderBuilder':
        """Сбрасывает все добавки (молоко, сиропы, сахар, лед)."""
        self._milk = "none"
        self._syrups.clear()
        self._sugar = 0
        self._iced = False
        return self
    
    def _calculate_price(self) -> float:
        """Вычисляет итоговую цену заказа."""
        if not self._base or not self._size:
            return 0.0
        
     
        price = self.BASE_PRICES[self._base]
        
       
        price *= self.SIZE_MULTIPLIERS[self._size]
        
       
        price += self.MILK_PRICES[self._milk]
        
        
        price += len(self._syrups) * self.SYRUP_PRICE
        
      
        if self._iced:
            price += self.ICED_PRICE
        
        return round(price, 2)
    
    def _generate_description(self) -> str:
        """Генерирует человекочитаемое описание заказа."""
        if not self._base or not self._size:
            return ""
        
        parts = [self._size, self._base]
        
        if self._milk != "none":
            milk_names = {
                "whole": "цельное",
                "skim": "обезжиренное",
                "oat": "овсяное",
                "soy": "соевое",
            }
            parts.append(f"с {milk_names.get(self._milk, self._milk)} молоком")
        
        if self._syrups:
            syrup_list = ", ".join(sorted(self._syrups))
            parts.append(f"+ сиропы: {syrup_list}")
        
        if self._iced:
            parts.append("(со льдом)")
        
        if self._sugar > 0:
            sugar_word = "ложка" if self._sugar == 1 else "ложки" if 2 <= self._sugar <= 4 else "ложек"
            parts.append(f"{self._sugar} {sugar_word} сахара")
        
        return " ".join(parts)
    
    def build(self) -> CoffeeOrder:
        """
        Создает новый CoffeeOrder на основе текущего состояния билдера.
        
        Raises:
            ValueError: если не указаны base или size, или нарушены лимиты
        """
        if not self._base:
            raise ValueError("Не указана основа кофе (base)")
        
        if not self._size:
            raise ValueError("Не указан размер кофе (size)")
        
        
        if self._sugar > self.MAX_SUGAR:
            raise ValueError(f"Сахар не может превышать {self.MAX_SUGAR} ложек")
        
        if len(self._syrups) > self.MAX_SYRUPS:
            raise ValueError(f"Количество сиропов не может превышать {self.MAX_SYRUPS}")
        
   
        order = CoffeeOrder(
            base=self._base,
            size=self._size,
            milk=self._milk,
            syrups=tuple(sorted(self._syrups)),
            sugar=self._sugar,
            iced=self._iced,
            price=self._calculate_price(),
            description=self._generate_description()
        )
        
        return order
    
    def __str__(self) -> str:
        """Строковое представление билдера."""
        if not self._base or not self._size:
            return "CoffeeOrderBuilder (не заполнен)"
        
        try:
            order = self.build()
            return f"CoffeeOrderBuilder -> {order.description}"
        except ValueError:
            return "CoffeeOrderBuilder (невалидное состояние)"


def run_tests():
    """Запуск тестов для проверки работы CoffeeOrderBuilder."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ COFFEE ORDER BUILDER")
    print("=" * 60)
    
   
    print("\n📋 ТЕСТ 1: Базовый заказ")
    builder = CoffeeOrderBuilder()
    order1 = (builder
              .set_base("latte")
              .set_size("medium")
              .set_milk("oat")
              .add_syrup("карамель")
              .add_syrup("ваниль")
              .set_sugar(2)
              .set_iced(True)
              .build())
    
    print(f"   Заказ: {order1}")
    print(f"   Цена: {order1.price}₽")
    print(f"   Описание: {order1.description}")
    
 
    assert order1.base == "latte"
    assert order1.size == "medium"
    assert order1.milk == "oat"
    assert "карамель" in order1.syrups
    assert "ваниль" in order1.syrups
    assert len(order1.syrups) == 2
    assert order1.sugar == 2
    assert order1.iced is True
    assert order1.price > 0
    print("   ✅ Базовый заказ прошел проверку")
    

    print("\n🔄 ТЕСТ 2: Переиспользование билдера")
    order2 = (builder
              .clear_extras()
              .set_base("espresso")
              .set_size("small")
              .build())
    
    print(f"   Order1 (не изменился): {order1}")
    print(f"   Order2 (новый): {order2}")
    
    assert order1.base == "latte"  
    assert order2.base == "espresso"
    assert order2.size == "small"
    assert order2.milk == "none"
    assert len(order2.syrups) == 0
    assert order2.sugar == 0
    assert order2.iced is False
    print("   ✅ Переиспользование работает корректно")
    
   
    print("\n🍯 ТЕСТ 3: Игнорирование дубликатов сиропов")
    builder.reset()
    order3 = (builder
              .set_base("cappuccino")
              .set_size("large")
              .add_syrup("карамель")
              .add_syrup("карамель")  
              .add_syrup("орех")
              .build())
    
    print(f"   Заказ: {order3}")
    print(f"   Сиропы: {order3.syrups}")
    print(f"   Количество сиропов: {len(order3.syrups)}")
    print(f"   Цена: {order3.price}₽")
    
    assert len(order3.syrups) == 2 
    assert "карамель" in order3.syrups
    assert "орех" in order3.syrups
    print("   ✅ Дубликаты игнорируются")
    

    print("\n⚠️ ТЕСТ 4: Валидация обязательных полей")
    builder.reset()
    
    try:
        builder.set_base("latte").build()
        assert False, "Должна была возникнуть ошибка из-за отсутствия size"
    except ValueError as e:
        print(f"   ✅ Ошибка при отсутствии size: {e}")
    
    try:
        builder.reset()
        builder.set_size("medium").build()
        assert False, "Должна была возникнуть ошибка из-за отсутствия base"
    except ValueError as e:
        print(f"   ✅ Ошибка при отсутствии base: {e}")
    
    
    print("\n🔢 ТЕСТ 5: Валидация лимитов")
    builder.reset()
    
    try:
        builder.set_base("latte").set_size("medium").set_sugar(6).build()
        assert False, "Должна была возникнуть ошибка из-за превышения сахара"
    except ValueError as e:
        print(f"   ✅ Ошибка при превышении сахара: {e}")
    
    try:
        builder.reset()
        (builder
         .set_base("latte")
         .set_size("medium")
         .add_syrup("a").add_syrup("b").add_syrup("c").add_syrup("d").add_syrup("e")
         .build())
        assert False, "Должна была возникнуть ошибка из-за превышения сиропов"
    except ValueError as e:
        print(f"   ✅ Ошибка при превышении сиропов: {e}")
    
    
    print("\n💰 ТЕСТ 6: Проверка расчета цены")
    
    
    builder.reset()
    order4 = builder.set_base("espresso").set_size("small").build()
    print(f"   Эспрессо small: {order4.price}₽ (ожидается 200)")
    assert order4.price == 200
    
    
    builder.reset()
    order5 = (builder
              .set_base("latte")
              .set_size("medium")
              .set_milk("oat")
              .build())
    expected = 300 * 1.2 + 60 
    print(f"   Латте medium с овсяным молоком: {order5.price}₽ (ожидается {expected})")
    assert order5.price == expected
    

    builder.reset()
    order6 = (builder
              .set_base("cappuccino")
              .set_size("large")
              .add_syrup("карамель")
              .add_syrup("ваниль")
              .set_iced(True)
              .build())
    expected = 320 * 1.4 + 2 * 40 + 0.2  # капучино 320 * large 1.4 + 2 сиропа + лед
    print(f"   Капучино large с 2 сиропами и льдом: {order6.price}₽ (ожидается {expected})")
    assert order6.price == expected
    

    print("\n📝 ТЕСТ 7: Формирование описания")
    builder.reset()
    order7 = (builder
              .set_base("latte")
              .set_size("medium")
              .set_milk("oat")
              .add_syrup("карамель")
              .set_sugar(1)
              .set_iced(True)
              .build())
    
    print(f"   Описание: {order7.description}")
    assert "medium latte" in order7.description
    assert "овсяное молоком" in order7.description or "oat молоком" in order7.description
    assert "карамель" in order7.description
    assert "со льдом" in order7.description
    assert "1 ложка сахара" in order7.description
    print("   ✅ Описание формируется корректно")
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    print("=" * 60)


def demo_order_examples():
    """Демонстрация примеров заказов."""
    print("\n" + "=" * 60)
    print("ПРИМЕРЫ ЗАКАЗОВ")
    print("=" * 60)
    
    builder = CoffeeOrderBuilder()
    

    order1 = builder.reset().set_base("espresso").set_size("small").build()
    print(f"\n1. {order1}")
    

    order2 = (builder
              .reset()
              .set_base("latte")
              .set_size("medium")
              .set_milk("oat")
              .build())
    print(f"2. {order2}")
    

    order3 = (builder
              .reset()
              .set_base("cappuccino")
              .set_size("large")
              .add_syrup("карамель")
              .set_iced(True)
              .build())
    print(f"3. {order3}")
    

    order4 = (builder
              .reset()
              .set_base("americano")
              .set_size("medium")
              .set_sugar(2)
              .build())
    print(f"4. {order4}")
    

    order5 = (builder
              .reset()
              .set_base("latte")
              .set_size("large")
              .set_milk("soy")
              .add_syrup("ваниль")
              .add_syrup("фундук")
              .set_sugar(1)
              .set_iced(True)
              .build())
    print(f"5. {order5}")


if __name__ == "__main__":
    run_tests()
    demo_order_examples()