import streamlit as st
from abc import ABC, abstractmethod
import json
from datetime import datetime

# ----------------------- Product Base Class -----------------------
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    @abstractmethod
    def __str__(self):
        pass

    def restock(self, amount):
        self._quantity_in_stock += amount

    def sell(self, quantity):
        if quantity > self._quantity_in_stock:
            raise Exception("Not enough stock to sell")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity_in_stock": self._quantity_in_stock,
        }

# ----------------------- Subclasses -----------------------
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, brand, warranty_years):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.brand = brand
        self.warranty_years = warranty_years

    def __str__(self):
        return f"🔌 Electronics: {self._name}, Brand: {self.brand}, Warranty: {self.warranty_years} years, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"brand": self.brand, "warranty_years": self.warranty_years})
        return data

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.expiry_date = expiry_date

    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d") < datetime.today()

    def __str__(self):
        return f"🍎 Grocery: {self._name}, Expiry: {self.expiry_date}, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"expiry_date": self.expiry_date})
        return data

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self.size = size
        self.material = material

    def __str__(self):
        return f"👕 Clothing: {self._name}, Size: {self.size}, Material: {self.material}, Stock: {self._quantity_in_stock}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"size": self.size, "material": self.material})
        return data

# ----------------------- Inventory Class -----------------------
class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if product._product_id in self._products:
            raise Exception("Duplicate product ID")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id in self._products:
            del self._products[product_id]

    def list_all_products(self):
        return [str(p) for p in self._products.values()]

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if p.__class__.__name__.lower() == product_type.lower()]

    def sell_product(self, product_id, quantity):
        self._products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        self._products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired:
            del self._products[pid]

    def save_to_file(self, filename):
        data = [p.to_dict() for p in self._products.values()]
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        for item in data:
            ptype = item["type"]
            if ptype == "Electronics":
                p = Electronics(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["brand"], item["warranty_years"])
            elif ptype == "Grocery":
                p = Grocery(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["expiry_date"])
            elif ptype == "Clothing":
                p = Clothing(item["product_id"], item["name"], item["price"], item["quantity_in_stock"], item["size"], item["material"])
            else:
                continue
            self._products[p._product_id] = p

# ----------------------- Streamlit UI -----------------------
st.set_page_config(page_title="Inventory Management System", layout="centered")

st.markdown("""
<style>
    /* Background */
    .stApp {
        background-color: #011c47;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #012b6a;
        color: white;
    }

    /* Headings */
    h1, h2, h3, .stSubheader {
        color: #69adf0 !important;
    }

    /* General Text Elements */
    p, span, div, label {
        color: #69adf0 !important;
    }

    /* Markdown text */
    .stMarkdown {
        color: white !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #ffeef3;
        color: #8ad3ed;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        background-color: #8ad3ed;
        transform: scale(1.03);
    }

    /* Input boxes */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stDateInput input {
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #69adf0;
        background-color: #011c47;
        color: white;
    }

    /* Footer */
    footer {
        visibility: hidden;
    }

    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #011c47;
        color: white;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-top: 2px solid #69adf0;
    }
</style>
""", unsafe_allow_html=True)


st.title("📦 Inventory Management System")

# Session State Setup
if 'inventory' not in st.session_state:
    st.session_state.inventory = Inventory()
    try:
        st.session_state.inventory.load_from_file("inventory.json")
    except:
        pass

inv = st.session_state.inventory
menu = st.sidebar.radio("📋 Menu", ["Add Product", "View Inventory", "Sell Product", "Restock Product", "Save", "Load", "Remove Expired"])

# ----------------------- App Pages -----------------------
if menu == "Add Product":
    st.header("➕ Add New Product")
    ptype = st.selectbox("Select Product Type", ["Electronics", "Grocery", "Clothing"])
    pid = st.text_input("Product ID")
    name = st.text_input("Product Name")
    price = st.number_input("Price", 0.0)
    quantity = st.number_input("Quantity", 0, step=1)

    if ptype == "Electronics":
        brand = st.text_input("Brand")
        warranty = st.number_input("Warranty (Years)", 0, step=1)
        if st.button("Add Electronics"):
            try:
                inv.add_product(Electronics(pid, name, price, quantity, brand, warranty))
                st.success("✅ Electronics product added!")
            except Exception as e:
                st.error(str(e))

    elif ptype == "Grocery":
        expiry = st.date_input("Expiry Date")
        if st.button("Add Grocery"):
            try:
                inv.add_product(Grocery(pid, name, price, quantity, expiry.strftime("%Y-%m-%d")))
                st.success("✅ Grocery product added!")
            except Exception as e:
                st.error(str(e))

    elif ptype == "Clothing":
        size = st.text_input("Size")
        material = st.text_input("Material")
        if st.button("Add Clothing"):
            try:
                inv.add_product(Clothing(pid, name, price, quantity, size, material))
                st.success("✅ Clothing product added!")
            except Exception as e:
                st.error(str(e))

elif menu == "View Inventory":
    st.header("📋 Current Inventory")
    for p in inv.list_all_products():
        st.write("- ", p)
    st.info(f"💰 **Total Inventory Value:** ${inv.total_inventory_value():,.2f}")

elif menu == "Sell Product":
    st.header("💸 Sell Product")
    pid = st.text_input("Enter Product ID to Sell")
    qty = st.number_input("Quantity", 0, step=1)
    if st.button("Sell"):
        try:
            inv.sell_product(pid, qty)
            st.success("✅ Product sold!")
        except Exception as e:
            st.error(str(e))

elif menu == "Restock Product":
    st.header("📦 Restock Product")
    pid = st.text_input("Enter Product ID to Restock")
    qty = st.number_input("Quantity", 0, step=1)
    if st.button("Restock"):
        try:
            inv.restock_product(pid, qty)
            st.success("✅ Product restocked!")
        except Exception as e:
            st.error(str(e))

elif menu == "Save":
    st.header("💾 Save Inventory")
    if st.button("Save to inventory.json"):
        inv.save_to_file("inventory.json")
        st.success("✅ Inventory saved to file.")

elif menu == "Load":
    st.header("📂 Load Inventory")
    if st.button("Load from inventory.json"):
        inv.load_from_file("inventory.json")
        st.success("✅ Inventory loaded from file.")

elif menu == "Remove Expired":
    st.header("🗑️ Remove Expired Products")
    if st.button("Remove Expired Grocery Items"):
        inv.remove_expired_products()
        st.success("✅ Expired items removed!")

# ----------------------- Footer -----------------------
st.markdown("---")
st.markdown("<footer>Created with Love by <b>Babar Bamsi</b></footer>", unsafe_allow_html=True)