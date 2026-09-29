from app.categories.models import CategoryType
from app.categories.schemas import CategoryCreate, CategoryUpdate


def test_category_create():
    category = CategoryCreate(name="Food", category_type=CategoryType.EXPENSE)
    assert category.name == "Food"
    assert category.category_type == CategoryType.EXPENSE
    assert category.parent_id is None


def test_category_create_with_parent():
    category = CategoryCreate(
        name="Restaurant",
        category_type=CategoryType.EXPENSE,
        parent_id=10,
    )
    assert category.parent_id == 10


def test_category_update_is_partial():
    update = CategoryUpdate(is_active=False)
    assert update.is_active is False
    assert update.name is None


def test_category_type_values():
    assert {item.value for item in CategoryType} == {"INCOME", "EXPENSE"}
