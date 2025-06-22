"""
Python Advanced: Домашнее задание 2

Разработать систему регистрации пользователя, используя Pydantic для валидации входных данных,
обработки вложенных структур и сериализации. Система должна обрабатывать данные в формате JSON.

Задачи:
1. Создать классы моделей данных с помощью Pydantic для пользователя и его адреса.

2. Реализовать функцию, которая принимает JSON строку, десериализует её в объекты Pydantic,
валидирует данные, и в случае успеха сериализует объект обратно в JSON и возвращает его.

3. Добавить кастомный валидатор для проверки соответствия возраста и статуса занятости пользователя.

4. Написать несколько примеров JSON строк для проверки различных сценариев валидации:
успешные регистрации и случаи, когда валидация не проходит (например возраст не соответствует статусу занятости).

Модели:
    Address: Должен содержать следующие поля:
        city: строка, минимум 2 символа.
        street: строка, минимум 3 символа.
        house_number: число, должно быть положительным.
    User: Должен содержать следующие поля:
        name: строка, должна быть только из букв, минимум 2 символа.
        age: число, должно быть между 0 и 120.
        email: строка, должна соответствовать формату email.
        is_employed: булево значение, статус занятости пользователя.
        address: вложенная модель адреса.

Валидация:
Проверка, что если пользователь указывает, что он занят (is_employed = true),
его возраст должен быть от 18 до 65 лет.

"""
#--------------------------------------------------------------------------------------------------------------------#

from pydantic import BaseModel, Field, EmailStr, ValidationError, field_validator, model_validator


#-------------- 1 --------------------------------#
class Address(BaseModel):
    city: str = Field(min_length=2) # ограничение на длину строки
    street: str = Field(min_length=3)
    house_number: int =  Field(gt=0) # положительное число


class User(BaseModel):
    name: str = Field(min_length=2, pattern=r"[A-Za-z\s]+$") # pattern --> только буквы
    age: int = Field(ge=0, le=120)
    email: EmailStr # встроенная валидация email от Pydantic
    is_employed: bool
    address: Address # вложенная модель

    # -------------- 3 --------------------------------#
    @model_validator(mode='after')
    def validate_employment_age(cls, model):
        if model.is_employed and not (18 <= model.age <= 65):
            raise ValueError("Employed users must be between 18 and 65 years old")
        return model



#-------------- 2 --------------------------------#
def validate_and_serialize_user(json_string: str) -> str:
    try:
        user = User.model_validate_json(json_string, strict=True)
        return user.model_dump_json(indent=2) # сериализация обратно в JSON
    except ValidationError as e:
        return f'Validation error: {e.errors()}'




# Пример JSON данных для регистрации пользователя

# 1. Успешная регистрация
user_1 = """
{
    "name": "John Doe",
    "age": 60,
    "email": "john.doe@example.com",
    "is_employed": true,
    "address": {
        "city": "New York",
        "street": "5th Avenue",
        "house_number": 123
    }
}
"""

# 2. Ошибка: возраст не соответствует занятости
user_2 = """
{
    "name": "Max Muller",
    "age": 17,
    "email": "max@example.com",
    "is_employed": true,
    "address": {
        "city": "Berlin",
        "street": "5th Avenue",
        "house_number": 14
    }
}
"""


# 3. Ошибка: имя содержит цифры
user_3 = """
{
    "name": "Mika--",
    "age": 24,
    "email": "mika98@example.com",
    "is_employed": true,
    "address": {
        "city": "Berlin",
        "street": "5th Avenue",
        "house_number": 14
    }
}
"""

# 4. Ошибка: house_number отрицательно
user_4 = """
{
    "name": "Bob",
    "age": 30,
    "email": "bob@example.com",
    "is_employed": true,
    "address": {
        "city": "Germany",
        "street": "5th Avenue",
        "house_number": -1
    }
}
"""



if __name__ == '__main__':
    print("=== VALID DATA ===")
    print(validate_and_serialize_user(user_1))

    print("=== INVALID AGE EMPLOYMENT ===")
    print(validate_and_serialize_user(user_2))

    print("=== INVALID NAME ===")
    print(validate_and_serialize_user(user_3))

    print("=== INVALID HOUSE NUMBER ===")
    print(validate_and_serialize_user(user_4))