from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


def get_product_or_404(product_id: int, db: Session) -> Product:
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing_product = (
        db.query(Product)
        .filter(Product.name.ilike(product.name))
        .first()
    )

    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="A product with this name already exists."
        )

    new_product = Product(
        name=product.name.strip(),
        description=product.description,
        price=product.price,
        available=product.available
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@router.get("/", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.name.asc()).all()


@router.get("/search/{product_name}", response_model=ProductResponse)
def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{product_name}%"))
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found."
        )

    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(product_id, db)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    product = get_product_or_404(product_id, db)
    update_data = product_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one product field to update."
        )

    new_name = update_data.get("name")
    if new_name is not None:
        cleaned_name = new_name.strip()
        if not cleaned_name:
            raise HTTPException(
                status_code=400,
                detail="Product name cannot be empty."
            )

        existing_product = (
            db.query(Product)
            .filter(Product.name.ilike(cleaned_name), Product.id != product.id)
            .first()
        )

        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="A product with this name already exists."
            )

        product.name = cleaned_name

    if "description" in update_data:
        product.description = update_data["description"]

    if "price" in update_data:
        product.price = update_data["price"]

    if "available" in update_data:
        product.available = update_data["available"]

    db.commit()
    db.refresh(product)

    return product
