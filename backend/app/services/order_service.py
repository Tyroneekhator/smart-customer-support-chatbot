import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.product import Product


class OrderService:
    """Order, cart, and product detection logic used by the chatbot.

    Stage 3 improvement:
    - One order can now contain many order items.
    - The chatbot adds products to a pending cart instead of creating one order row per product.
    - Order totals are saved in the database.
    - Customer contact, delivery method, address, and notes can be stored on the order.
    - Confirm/cancel applies to the current pending cart for the chat session.
    """

    ALLOWED_STATUSES = [
        "pending",
        "confirmed",
        "preparing",
        "out_for_delivery",
        "completed",
        "cancelled",
    ]

    NUMBER_WORDS = {
        "zero": 0,
        "one": 1,
        "a": 1,
        "an": 1,
        "single": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "dozen": 12,
    }

    ORDER_WORDS = [
        "i want",
        "i need",
        "i would like",
        "i'd like",
        "order",
        "buy",
        "purchase",
        "get me",
        "can i have",
        "can i order",
        "please add",
        "add",
        "give me",
        "make it",
        "i will take",
        "i'll take",
    ]

    PRODUCT_ALIAS_OVERRIDES = {
        "Chocolate Chip Cookie": [
            "chocolate chip",
            "choc chip",
            "chocolate cookie",
            "choc cookie",
            "chip cookie",
            "chocolate chips",
        ],
        "Shortbread Cookie": ["shortbread", "short bread"],
        "Macaron Cookie": ["macaron", "macarons", "french macaron", "french macarons"],
        "Macaroon Cookie": ["macaroon", "macaroons", "coconut macaroon", "coconut macaroons"],
        "Biscotti Cookie": ["biscotti", "biscottis"],
        "Sugar Cookie": ["sugar", "sugar cookie", "sugar cookies"],
        "Oatmeal Raisin Cookie": [
            "oatmeal raisin",
            "oatmeal",
            "raisin",
            "oatmeal cookie",
            "raisin cookie",
        ],
        "Gingerbread Cookie": ["gingerbread", "ginger", "ginger bread"],
    }

    def clean_text(self, text: str) -> str:
        cleaned = text.lower().strip()
        cleaned = cleaned.replace("’", "'")
        cleaned = re.sub(r"[^a-z0-9@.'+\-\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def get_available_products(self, db: Session) -> List[Product]:
        return (
            db.query(Product)
            .filter(Product.available == True)  # noqa: E712
            .order_by(Product.name.asc())
            .all()
        )

    def build_aliases(self, product: Product) -> List[str]:
        aliases = set()
        product_name = self.clean_text(product.name)
        aliases.add(product_name)

        without_cookie = re.sub(r"\bcookies?\b", "", product_name).strip()
        if without_cookie:
            aliases.add(without_cookie)

        current_aliases = list(aliases)
        for alias in current_aliases:
            aliases.add(alias.replace(" cookie", " cookies"))
            aliases.add(alias.replace(" cookies", " cookie"))
            if not alias.endswith("s"):
                aliases.add(f"{alias}s")

        for alias in self.PRODUCT_ALIAS_OVERRIDES.get(product.name, []):
            aliases.add(self.clean_text(alias))

        return sorted(alias for alias in aliases if alias)

    def get_product_catalog(self, db: Session) -> List[Dict[str, Any]]:
        catalog = []

        for product in self.get_available_products(db):
            catalog.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "aliases": self.build_aliases(product),
                }
            )

        return catalog

    def exact_alias_matches(self, cleaned_message: str, aliases: List[str]) -> List[Dict[str, Any]]:
        matches = []

        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            for match in re.finditer(pattern, cleaned_message):
                matches.append(
                    {
                        "alias": alias,
                        "start": match.start(),
                        "end": match.end(),
                        "score": 1.0,
                        "match_type": "exact",
                    }
                )

        return matches

    def fuzzy_product_match(self, cleaned_message: str, catalog: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        message_tokens = cleaned_message.split()
        best_match = None
        best_score = 0.0

        for product in catalog:
            for alias in product["aliases"]:
                alias_tokens = alias.split()
                token_count = len(alias_tokens)

                if token_count == 0 or token_count > len(message_tokens):
                    continue

                for index in range(0, len(message_tokens) - token_count + 1):
                    phrase = " ".join(message_tokens[index:index + token_count])
                    score = SequenceMatcher(None, phrase, alias).ratio()

                    if score > best_score:
                        start = len(" ".join(message_tokens[:index]))
                        if start > 0:
                            start += 1

                        best_score = score
                        best_match = {
                            "product": product,
                            "alias": alias,
                            "start": start,
                            "end": len(" ".join(message_tokens[:index + token_count])),
                            "score": score,
                            "match_type": "fuzzy",
                        }

        if best_match and best_score >= 0.84:
            return best_match

        return None

    def detect_product(self, db: Session, message: str) -> Optional[Dict[str, Any]]:
        cleaned_message = self.clean_text(message)
        catalog = self.get_product_catalog(db)
        best_product = None
        best_alias_length = 0

        for product in catalog:
            matches = self.exact_alias_matches(cleaned_message, product["aliases"])
            if not matches:
                continue

            longest_alias = max(matches, key=lambda item: len(item["alias"]))
            if len(longest_alias["alias"]) > best_alias_length:
                best_alias_length = len(longest_alias["alias"])
                best_product = product

        if best_product:
            return best_product

        fuzzy_match = self.fuzzy_product_match(cleaned_message, catalog)
        if fuzzy_match:
            return fuzzy_match["product"]

        return None

    def contains_order_language(self, cleaned_message: str) -> bool:
        return any(word in cleaned_message for word in self.ORDER_WORDS)

    def contains_quantity_language(self, cleaned_message: str) -> bool:
        if re.search(r"\b\d+\b", cleaned_message):
            return True

        return any(word in cleaned_message.split() for word in self.NUMBER_WORDS)

    def parse_quantity_value(self, value: str) -> int:
        value = value.lower().strip()

        if value.isdigit():
            return int(value)

        return self.NUMBER_WORDS.get(value, 1)

    def detect_quantity_near_match(self, cleaned_message: str, match_start: int, match_end: int) -> int:
        number_pattern = r"(?:\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|dozen|a|an|single)"

        before_text = cleaned_message[max(0, match_start - 60):match_start]
        separator_positions = [before_text.rfind(" and "), before_text.rfind(" then "), before_text.rfind(",")]
        last_separator = max(separator_positions)
        if last_separator != -1:
            before_text = before_text[last_separator + 1:]

        before_matches = re.findall(rf"\b({number_pattern})\b(?:\s+\w+){{0,2}}\s*$", before_text)

        if before_matches:
            quantity = self.parse_quantity_value(before_matches[-1])
            return max(quantity, 1)

        after_text = cleaned_message[match_end:match_end + 25]
        after_match = re.search(rf"^\s*(?:x|times)?\s*\b({number_pattern})\b", after_text)

        if after_match:
            quantity = self.parse_quantity_value(after_match.group(1))
            return max(quantity, 1)

        return 1

    def detect_order_items(self, db: Session, message: str) -> List[Dict[str, Any]]:
        cleaned_message = self.clean_text(message)
        catalog = self.get_product_catalog(db)

        if not catalog:
            return []

        looks_like_order = self.contains_order_language(cleaned_message)
        has_quantity = self.contains_quantity_language(cleaned_message)

        detected_items = []
        used_product_names = set()

        for product in catalog:
            matches = self.exact_alias_matches(cleaned_message, product["aliases"])

            if not matches:
                continue

            best_match = max(matches, key=lambda item: len(item["alias"]))
            quantity = self.detect_quantity_near_match(
                cleaned_message,
                best_match["start"],
                best_match["end"],
            )

            if not looks_like_order and not has_quantity:
                continue

            if product["name"] in used_product_names:
                continue

            detected_items.append(
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "match_type": best_match["match_type"],
                }
            )
            used_product_names.add(product["name"])

        if detected_items:
            return detected_items

        fuzzy_match = self.fuzzy_product_match(cleaned_message, catalog)
        if fuzzy_match and (looks_like_order or has_quantity):
            quantity = self.detect_quantity_near_match(
                cleaned_message,
                fuzzy_match["start"],
                fuzzy_match["end"],
            )
            product = fuzzy_match["product"]

            return [
                {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "match_type": fuzzy_match["match_type"],
                }
            ]

        return []

    def get_product_for_order_item(self, db: Session, item: Dict[str, Any]) -> Optional[Product]:
        product_id = item.get("product_id")
        product_name = item.get("product_name")

        query = db.query(Product).filter(Product.available == True)  # noqa: E712

        if product_id:
            return query.filter(Product.id == product_id).first()

        if product_name:
            return query.filter(Product.name.ilike(product_name)).first()

        return None

    def get_pending_order(self, db: Session, session_id: str) -> Optional[Order]:
        return (
            db.query(Order)
            .filter(Order.session_id == session_id)
            .filter(Order.status == "pending")
            .order_by(Order.created_at.desc())
            .first()
        )

    def get_or_create_pending_order(self, db: Session, session_id: str) -> Order:
        order = self.get_pending_order(db, session_id)

        if order:
            return order

        order = Order(
            session_id=session_id,
            status="pending",
            delivery_method="pickup",
            subtotal=0.0,
            total_price=0.0,
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def refresh_order_totals(self, order: Order) -> Order:
        subtotal = sum(item.line_total for item in order.items)
        order.subtotal = round(subtotal, 2)
        order.total_price = round(subtotal, 2)
        order.updated_at = datetime.utcnow()
        return order

    def add_items_to_pending_order(self, db: Session, session_id: str, items: List[Dict[str, Any]]) -> Order:
        order = self.get_or_create_pending_order(db, session_id)

        for item in items:
            product = self.get_product_for_order_item(db, item)

            if product:
                product_id = product.id
                product_name = product.name
                unit_price = float(product.price)
            else:
                product_id = item.get("product_id")
                product_name = item["product_name"]
                unit_price = float(item.get("unit_price", 0.0))

            quantity = max(int(item.get("quantity", 1)), 1)
            existing_item = None

            for order_item in order.items:
                if order_item.product_id == product_id or order_item.product_name.lower() == product_name.lower():
                    existing_item = order_item
                    break

            if existing_item:
                existing_item.quantity += quantity
                existing_item.unit_price = unit_price
                existing_item.line_total = round(existing_item.quantity * unit_price, 2)
            else:
                order.items.append(
                    OrderItem(
                        product_id=product_id,
                        product_name=product_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        line_total=round(quantity * unit_price, 2),
                    )
                )

        self.refresh_order_totals(order)
        db.commit()
        db.refresh(order)
        return order

    def create_manual_order(self, db: Session, order_data: Dict[str, Any]) -> Order:
        order = Order(
            session_id=order_data["session_id"],
            status="pending",
            customer_name=order_data.get("customer_name"),
            customer_email=order_data.get("customer_email"),
            customer_phone=order_data.get("customer_phone"),
            delivery_method=order_data.get("delivery_method", "pickup"),
            delivery_address=order_data.get("delivery_address"),
            notes=order_data.get("notes"),
            subtotal=0.0,
            total_price=0.0,
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        items = [item.model_dump() if hasattr(item, "model_dump") else dict(item) for item in order_data["items"]]
        return self.add_items_to_pending_order(db, order.session_id, items)

    def extract_customer_details(self, message: str) -> Dict[str, str]:
        original_message = message.strip()
        cleaned_message = self.clean_text(message)
        details: Dict[str, str] = {}

        email_match = re.search(r"[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+", original_message)
        if email_match:
            details["customer_email"] = email_match.group(0)

        phone_match = re.search(r"(?:\+?\d[\d\s\-]{6,}\d)", original_message)
        if phone_match:
            details["customer_phone"] = re.sub(r"\s+", " ", phone_match.group(0)).strip()

        name_match = re.search(
            r"\b(?:my name is|name is|i am|i'm)\s+([a-zA-Z][a-zA-Z\s'\-]{1,40})",
            original_message,
            flags=re.IGNORECASE,
        )
        if name_match:
            name = name_match.group(1).strip(" .,!?")
            stop_words = [" and ", " my ", " phone ", " email ", " address ", " delivery "]
            lower_name = name.lower()
            cut_positions = [lower_name.find(word) for word in stop_words if lower_name.find(word) != -1]
            if cut_positions:
                name = name[:min(cut_positions)].strip(" .,!?")
            if name and len(name.split()) <= 4:
                details["customer_name"] = name.title()

        if "pickup" in cleaned_message or "collect" in cleaned_message or "collection" in cleaned_message:
            details["delivery_method"] = "pickup"

        address_match = re.search(
            r"\b(?:deliver to|delivery to|send to|address is|my address is)\s+(.+)$",
            original_message,
            flags=re.IGNORECASE,
        )
        if address_match:
            details["delivery_method"] = "delivery"
            details["delivery_address"] = address_match.group(1).strip(" .")
        elif "delivery" in cleaned_message or "deliver" in cleaned_message:
            details["delivery_method"] = "delivery"

        return details

    def update_order_details(self, db: Session, order: Order, details: Dict[str, Optional[str]]) -> Order:
        allowed_fields = [
            "customer_name",
            "customer_email",
            "customer_phone",
            "delivery_method",
            "delivery_address",
            "notes",
        ]

        for field in allowed_fields:
            value = details.get(field)
            if value is not None and value != "":
                setattr(order, field, value)

        order.updated_at = datetime.utcnow()
        self.refresh_order_totals(order)
        db.commit()
        db.refresh(order)
        return order

    def update_order_status(self, db: Session, order: Order, status: str) -> Order:
        order.status = status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
        return order

    def confirm_pending_order(self, db: Session, session_id: str) -> Optional[Order]:
        order = self.get_pending_order(db, session_id)

        if not order or not order.items:
            return None

        return self.update_order_status(db, order, "confirmed")

    def cancel_pending_order(self, db: Session, session_id: str) -> Optional[Order]:
        order = self.get_pending_order(db, session_id)

        if not order:
            return None

        return self.update_order_status(db, order, "cancelled")

    # Backwards-compatible method names used by older code/tests.
    def create_order(self, db: Session, session_id: str, product_name: str, quantity: int):
        product = db.query(Product).filter(Product.name.ilike(product_name)).first()
        item = {
            "product_id": product.id if product else None,
            "product_name": product.name if product else product_name,
            "quantity": quantity,
            "unit_price": float(product.price) if product else 0.0,
        }
        return self.add_items_to_pending_order(db, session_id, [item])

    def create_orders(self, db: Session, session_id: str, items: List[Dict[str, Any]]) -> List[Order]:
        return [self.add_items_to_pending_order(db, session_id, items)]

    def get_pending_orders(self, db: Session, session_id: str) -> List[Order]:
        order = self.get_pending_order(db, session_id)
        return [order] if order else []

    def confirm_pending_orders(self, db: Session, session_id: str) -> List[Order]:
        order = self.confirm_pending_order(db, session_id)
        return [order] if order else []

    def cancel_pending_orders(self, db: Session, session_id: str) -> List[Order]:
        order = self.cancel_pending_order(db, session_id)
        return [order] if order else []

    def confirm_latest_order(self, db: Session, session_id: str):
        return self.confirm_pending_order(db, session_id)

    def cancel_latest_order(self, db: Session, session_id: str):
        return self.cancel_pending_order(db, session_id)
