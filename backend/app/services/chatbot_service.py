import uuid
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.order import Order, OrderItem
from app.services.intent_service import IntentService
from app.services.order_service import OrderService


class ChatbotService:
    def __init__(self):
        self.intent_service = IntentService()
        self.order_service = OrderService()

    def save_message(
        self,
        db: Session,
        session_id: str,
        sender: str,
        message: str,
        intent: str = None,
    ):
        chat_message = ChatMessage(
            session_id=session_id,
            sender=sender,
            message=message,
            intent=intent,
        )

        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)

        return chat_message

    def format_product_quantity(self, quantity: int, product_name: str) -> str:
        if quantity == 1:
            return f"{quantity} {product_name}"

        if product_name.endswith("Cookie"):
            return f"{quantity} {product_name}s"

        return f"{quantity} {product_name}"

    def format_order_items_summary(self, items: List[OrderItem]) -> str:
        summary_parts = []

        for item in items:
            summary_parts.append(
                f"{self.format_product_quantity(item.quantity, item.product_name)} (£{item.line_total:.2f})"
            )

        if not summary_parts:
            return "no items"

        if len(summary_parts) == 1:
            return summary_parts[0]

        return ", ".join(summary_parts[:-1]) + f", and {summary_parts[-1]}"

    def format_order_summary(self, order: Order) -> str:
        return self.format_order_items_summary(order.items)

    def format_customer_details(self, order: Order) -> str:
        details = []

        if order.customer_name:
            details.append(f"Name: {order.customer_name}")
        if order.customer_phone:
            details.append(f"Phone: {order.customer_phone}")
        if order.customer_email:
            details.append(f"Email: {order.customer_email}")
        if order.delivery_method:
            details.append(f"Method: {order.delivery_method}")
        if order.delivery_address:
            details.append(f"Address: {order.delivery_address}")

        if not details:
            return ""

        return " Details saved: " + "; ".join(details) + "."

    def is_generic_cookie_order_request(self, message: str) -> bool:
        """Detect broad buying requests that do not name a specific product yet.

        Example: "I want to buy cookies" should show the menu and ask the
        customer which cookie they want, instead of falling back or creating an
        empty order.
        """
        cleaned_message = self.order_service.clean_text(message)
        generic_cookie_terms = [
            "cookie",
            "cookies",
            "biscuit",
            "biscuits",
            "treat",
            "treats",
        ]

        has_order_language = self.order_service.contains_order_language(cleaned_message)
        message_words = cleaned_message.split()
        mentions_generic_cookie = any(
            term in message_words
            for term in generic_cookie_terms
        )

        return has_order_language and mentions_generic_cookie

    def is_order_again_request(self, message: str) -> bool:
        """Detect when a customer wants to start another order.

        Example: after confirming an order, "I would like to order again"
        should show the menu again and ask the customer what they want next.
        """
        cleaned_message = self.order_service.clean_text(message)
        reorder_phrases = [
            "another order",
            "buy again",
            "buy more",
            "can i order again",
            "i want to order again",
            "i would like to order again",
            "i'd like to order again",
            "new order",
            "order again",
            "order another",
            "order more",
            "place another order",
            "start another order",
        ]

        return any(phrase in cleaned_message for phrase in reorder_phrases)

    def is_not_interested_request(self, message: str) -> bool:
        """Detect when the customer is saying they are not interested.

        This is checked before positive interest phrases so messages like
        "I am not interested in cookies" do not accidentally open the menu.
        The common typo "intrested" is supported too.
        """
        cleaned_message = self.order_service.clean_text(message)
        not_interested_phrases = [
            "i am not interested",
            "i am not intrested",
            "i'm not interested",
            "i'm not intrested",
            "im not interested",
            "im not intrested",
            "not interested",
            "not intrested",
            "no longer interested",
            "no longer intrested",
            "not interested in cookies",
            "not intrested in cookies",
            "i dont want cookies",
            "i don't want cookies",
            "i do not want cookies",
            "i dont want to order",
            "i don't want to order",
            "i do not want to order",
        ]

        return any(phrase in cleaned_message for phrase in not_interested_phrases)

    def is_interested_request(self, message: str) -> bool:
        """Detect when the customer becomes interested and should see the menu.

        Examples: "I am interested", "I am intrested",
        "please I like to order cookies", or similar buying language.
        """
        cleaned_message = self.order_service.clean_text(message)

        if self.is_not_interested_request(cleaned_message):
            return False

        interested_phrases = [
            "i am interested",
            "i am intrested",
            "i'm interested",
            "i'm intrested",
            "im interested",
            "im intrested",
            "now i am interested",
            "now i am intrested",
            "i like to order cookies",
            "i would like to order cookies",
            "please i like to order cookies",
            "please i would like to order cookies",
            "i want to order cookies",
            "i want to buy cookies",
            "i want cookies",
            "i need cookies",
            "i would like cookies",
            "i'd like cookies",
            "let me see the menu",
        ]

        return any(phrase in cleaned_message for phrase in interested_phrases)

    # Backwards-compatible helpers for older tests/code.
    def get_product_price_map(self, db: Session) -> Dict[str, float]:
        products = self.order_service.get_available_products(db)
        return {product.name: product.price for product in products}

    def calculate_orders_total(self, db: Session, orders: List[Order]) -> float:
        return sum(order.total_price for order in orders)

    def format_orders_summary(self, db: Session, orders: List[Order]) -> str:
        if not orders:
            return "no items"

        if len(orders) == 1:
            return self.format_order_summary(orders[0])

        return ", ".join(self.format_order_summary(order) for order in orders)

    def process_message(self, db: Session, user_message: str, session_id: str = None):
        cleaned_message = user_message.strip()

        if not session_id:
            session_id = str(uuid.uuid4())

        if not cleaned_message:
            reply = "Please enter a message so I can help you."
            intent = "empty_message"

            self.save_message(
                db=db,
                session_id=session_id,
                sender="bot",
                message=reply,
                intent=intent,
            )

            return {
                "reply": reply,
                "intent": intent,
                "session_id": session_id,
            }

        self.save_message(
            db=db,
            session_id=session_id,
            sender="user",
            message=cleaned_message,
        )

        intent_result = self.intent_service.detect_intent(cleaned_message)
        intent = intent_result["intent"]
        order_items = self.order_service.detect_order_items(db, cleaned_message)
        customer_details = self.order_service.extract_customer_details(cleaned_message)
        pending_order = self.order_service.get_pending_order(db, session_id)

        if self.is_not_interested_request(cleaned_message) and not order_items:
            intent = "not_interested"
            reply = "Ok, please let me know when you are interested."

        elif self.is_order_again_request(cleaned_message) and not order_items:
            intent = "menu"
            reply = self.get_order_again_menu_response(db)

        elif self.is_interested_request(cleaned_message) and not order_items:
            intent = "menu"
            reply = self.get_interested_menu_response(db)

        elif self.is_generic_cookie_order_request(cleaned_message) and not order_items:
            intent = "menu"
            reply = self.get_menu_response(db)

        elif intent == "price":
            reply = self.get_price_response(db, cleaned_message)

        elif intent == "menu":
            mentioned_product = self.order_service.detect_product(db, cleaned_message)

            if mentioned_product:
                intent = "product_info"
                reply = (
                    f"Yes, we have {mentioned_product['name']} for £{mentioned_product['price']:.2f} each. "
                    f"To order, type something like: I want 2 {mentioned_product['name']}s."
                )
            else:
                reply = self.get_menu_response(db)

        elif order_items:
            order = self.order_service.add_items_to_pending_order(
                db=db,
                session_id=session_id,
                items=order_items,
            )

            if customer_details:
                order = self.order_service.update_order_details(db, order, customer_details)

            order_summary = self.format_order_summary(order)
            intent = "order"
            reply = (
                f"Great choice. Your pending order now contains {order_summary}. "
                f"Total: £{order.total_price:.2f}. "
                "Type 'confirm' to place the order, 'cancel' to cancel it, or add another item. "
                "You can also send your name, phone number, email, and delivery address."
            )

        elif intent == "confirm_order":
            confirmed_order = self.order_service.confirm_pending_order(db, session_id)

            if confirmed_order:
                order_summary = self.format_order_summary(confirmed_order)
                reply = (
                    f"Your order has been confirmed. You ordered {order_summary}. "
                    f"Total: £{confirmed_order.total_price:.2f}."
                    f"{self.format_customer_details(confirmed_order)} "
                    "Thank you for shopping with CookieBot."
                )
            else:
                reply = (
                    "You do not have any pending order to confirm. "
                    "You can place an order by typing something like: I want 2 chocolate chip cookies."
                )

        elif intent == "cancel_order":
            cancelled_order = self.order_service.cancel_pending_order(db, session_id)

            if cancelled_order:
                order_summary = self.format_order_summary(cancelled_order)
                reply = f"Your pending order for {order_summary} has been cancelled."
            else:
                reply = "You do not have any pending order to cancel."

        elif customer_details and pending_order:
            updated_order = self.order_service.update_order_details(db, pending_order, customer_details)
            intent = "order_details"
            reply = (
                "Thanks, I have updated your pending order details."
                f"{self.format_customer_details(updated_order)} "
                f"Your current order total is £{updated_order.total_price:.2f}. Type 'confirm' when you are ready."
            )

        else:
            mentioned_product = self.order_service.detect_product(db, cleaned_message)

            if mentioned_product:
                intent = "product_info"
                reply = (
                    f"Yes, we have {mentioned_product['name']} for £{mentioned_product['price']:.2f} each. "
                    f"To order, type something like: I want 2 {mentioned_product['name']}s."
                )
            else:
                reply = intent_result["reply"]

        self.save_message(
            db=db,
            session_id=session_id,
            sender="bot",
            message=reply,
            intent=intent,
        )

        return {
            "reply": reply,
            "intent": intent,
            "session_id": session_id,
        }

    def get_price_response(self, db: Session, message: str):
        product = self.order_service.detect_product(db, message)

        if product:
            return f"{product['name']} costs £{product['price']:.2f} each."

        catalog = self.order_service.get_product_catalog(db)

        if not catalog:
            return "I could not find any available products at the moment."

        product_prices = [
            f"{product['name']} (£{product['price']:.2f})"
            for product in catalog
        ]

        return "Here are our current prices: " + ", ".join(product_prices) + "."

    def format_menu_items(self, db: Session) -> List[str]:
        catalog = self.order_service.get_product_catalog(db)
        return [
            f"{product['name']} (£{product['price']:.2f})"
            for product in catalog
        ]

    def get_menu_response(self, db: Session):
        product_names = self.format_menu_items(db)

        if not product_names:
            return "There are no available products on the menu at the moment."

        return (
            "Sure, here is our current cookie menu: "
            + ", ".join(product_names)
            + ". Which cookies would you like to buy? "
            "You can type something like: I want 2 Chocolate Chip Cookies."
        )

    def get_order_again_menu_response(self, db: Session):
        product_names = self.format_menu_items(db)

        if not product_names:
            return "Yes please, but there are no available products on the menu at the moment."

        return (
            "Yes please, here is the menu: "
            + ", ".join(product_names)
            + ". What cookies would you like to order this time? "
            "You can type something like: I want 2 Chocolate Chip Cookies."
        )

    def get_interested_menu_response(self, db: Session):
        product_names = self.format_menu_items(db)

        if not product_names:
            return "Yes, but there are no available products on the menu at the moment."

        return (
            "Yes please, here is the menu: "
            + ", ".join(product_names)
            + ". What cookies would you like to buy? "
            "You can type something like: I want 2 Chocolate Chip Cookies."
        )
