import tkinter as tk
from tkinter import Label, Text, Button, Listbox, Scrollbar, messagebox, ttk, Menu, filedialog, Radiobutton, IntVar, Entry, StringVar, OptionMenu, Toplevel
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

class CheckoutWindow:
    def __init__(self, master, cart_items, total_price):
        self.master = master
        self.cart_items = cart_items
        self.total_price = total_price

        self.master.title("Checkout")
        w = master.winfo_screenwidth()
        h = master.winfo_screenheight()
        master.geometry(f"{w}x{h}")
        self.master.configure(bg="#C8C4DF")

        self.label_items = Label(master, text=f"You're purchasing: {', '.join(cart_items)}", font=("Courier", 14))
        self.label_items.pack(pady=(20, 10))

        self.label_price = Label(master, text=f"Total Price: ${total_price:.2f}", font=("Courier", 14))
        self.label_price.pack()

        self.label_name = Label(master, text="Name:", font=("Courier", 12))
        self.label_name.pack(pady=10)
        self.entry_name = Entry(master)
        self.entry_name.pack()

        self.label_address = Label(master, text="Address:", font=("Courier", 12))
        self.label_address.pack(pady=10)
        self.entry_address = Entry(master)
        self.entry_address.pack()

        self.label_payment = Label(master, text="Payment Type:", font=("Courier", 12))
        self.label_payment.pack(pady=10)
        self.payment_options = ["Credit Card", "Debit Card", "PayPal"]
        self.payment_var = StringVar(master)
        self.payment_var.set(self.payment_options[0])
        self.payment_dropdown = OptionMenu(master, self.payment_var, *self.payment_options)
        self.payment_dropdown.pack()

        self.place_order_button = Button(master, text="Place Order", command=self.place_order, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.place_order_button.pack(pady=20)

    def place_order(self):
        name = self.entry_name.get()
        address = self.entry_address.get()
        payment_type = self.payment_var.get()

        if not name or not address:
            messagebox.showerror("Error", "Please fill in both name and address.")
            return

        messagebox.showinfo("Order Placed", "Your order will arrive in 2-3 weeks.")
        self.master.destroy()

def open_url(url):
    response = None
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
    except requests.exceptions.ConnectionError as e:
        print("Error connecting:", e)
    except requests.exceptions.Timeout as e:
        print("Timeout Error:", e)
    except requests.exceptions.RequestException as e:
        print("Request exception:", e)

    return response

def get_categories(base_url):
    response = open_url(base_url)
    categories = {}
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        category_links = soup.find("div", class_="side_categories").find("ul").find_all("a")
        for link in category_links:
            category_url = link.get("href")
            category = link.text.strip()
            categories[category] = category_url
    return categories

def get_exchange_rate():
    url = "https://www.x-rates.com/calculator/?from=GBP&to=USD"
    response = open_url(url)
    exchange_rate = None
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        rate_div = soup.find("span", class_="ccOutputRslt")
        if rate_div:
            rate_text = rate_div.text.strip()
            rate_numeric = "".join(filter(lambda x: x.isdigit() or x == ".", rate_text))
            exchange_rate = float(rate_numeric)
    return exchange_rate

def get_books(topic_url):
    base_url = "http://books.toscrape.com/"
    books = []

    while True:
        url = urljoin(base_url, topic_url)
        response = open_url(url)
        if not response or response.status_code != 200:
            print(f"Failed to fetch books for '{topic_url}'.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        book_divs = soup.find_all("article", class_="product_pod")

        exchange_rate = get_exchange_rate()

        if exchange_rate is None:
            print("Failed to fetch the exchange rate. Prices will be in GBP.")
            return []

        for div in book_divs:
            title = div.h3.a["title"]
            price = float(div.select_one(".price_color").get_text()[2:])
            star_rating_class = div.select_one(".star-rating")["class"][1]
            star_rating = star_rating_class.split("-")[-1]
            price_usd = price * exchange_rate
            books.append({"title": title, "price_usd": price_usd, "star_rating": star_rating})

        next_page_link = soup.select_one(".next a")
        if not next_page_link:
            break
        next_href = next_page_link.get("href")
        topic_url = urljoin(topic_url, next_href)

    return books

class WebScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Book Scraper")
        w = master.winfo_screenwidth()
        h = master.winfo_screenheight()
        master.geometry(f"{w}x{h}")
        self.master.configure(bg="#C8C4DF")

        self.header_label = Label(self.master, text="GUI Books 🐌", font=("Courier", 30), height=2, bg="#6A5ACD", fg="white")
        self.header_label.grid(row=0, column=0, columnspan=7, pady=(0, 0), sticky="ew")

        self.base_url = "http://books.toscrape.com/"

        self.label_url = Label(self.master, text="Enter the URL you want to scrape:", font=("Courier", 14), bg="white", fg="black")
        self.label_url.grid(row=1, column=0, sticky="w", pady=5)
        self.textbox_url = Text(self.master, height=1, width=50, font=("Courier", 16), bg="white", fg="black", relief="raised")
        self.textbox_url.insert(tk.END, self.base_url)
        self.textbox_url.grid(row=1, column=1)

        self.get_topics_button = Button(self.master, text="Get Topics", command=self.get_topics, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.get_topics_button.grid(row=1, column=2, pady=5)

        self.label_exchange_rate = Label(self.master, text="Current Exchange Rate: -", font=("Courier", 14), bg="black", fg="white")
        self.label_exchange_rate.grid(row=2, column=3, pady=5, padx=10)

        self.get_exchange_rate_button = Button(self.master, text="Get Exchange Rate", command=self.get_exchange_rate, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.get_exchange_rate_button.grid(row=1, column=3, pady=5)

        self.label_avail_books = Label(self.master, text="Available Books", font=("Courier", 16), bg="white", fg="black")
        self.label_avail_books.grid(row=2, column=1)

        self.scrape_books_button = Button(self.master, text="Scrape Books", command=self.scrape_books, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.scrape_books_button.grid(row=3, column=2, columnspan=1, padx=20)

        self.topics_listbox = Listbox(self.master, width=65, selectmode="multiple", font=("Courier", 14), fg="#36013F", bg="lavender")
        self.topics_listbox.grid(row=3, column=1, columnspan=4, pady=15, sticky="w")
        self.scrollbar = Scrollbar(self.master, orient="vertical", command=self.topics_listbox.yview)
        self.scrollbar.grid(row=3, column=2, sticky="nsw", pady=15, padx=0)
        self.topics_listbox.config(yscrollcommand=self.scrollbar.set)

        self.price_range_frame = tk.Frame(self.master)
        self.price_range_frame.grid(row=5, column=3, rowspan=1, padx=40, pady=15, sticky="nsew")

        self.label_price_range = Label(self.price_range_frame, text="Price Range", bg="#6A5ACD", fg="white", font=("courier",16))
        self.label_price_range.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        self.price_range_var = IntVar()
        self.radio_button_all_price = Radiobutton(self.price_range_frame, text="All", variable=self.price_range_var, value= 0, command=self.scrape_books)
        self.radio_button_all_price.grid(row=1, column=0, sticky= "w", padx=5, pady=5)
        self.radio_button_low = Radiobutton(self.price_range_frame, text="Low ($0-$10)", variable=self.price_range_var, value=1, command=self.scrape_books)
        self.radio_button_low.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.radio_button_medium = Radiobutton(self.price_range_frame, text="Medium ($10-$20)", variable=self.price_range_var, value=2, command=self.scrape_books)
        self.radio_button_medium.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.radio_button_high = Radiobutton(self.price_range_frame, text="High ($20+)", variable=self.price_range_var, value=3, command=self.scrape_books)
        self.radio_button_high.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        self.star_rating_frame = tk.Frame(self.master)
        self.star_rating_frame.grid(row=5, column=4, rowspan=1, padx=20, pady=15, sticky="nsew")

        self.label_star_rating = Label(self.star_rating_frame, text="Star Rating", bg="#6A5ACD", fg="white", font=("courier",16))
        self.label_star_rating.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        self.star_rating_var = IntVar()
        self.radio_button_all = Radiobutton(self.star_rating_frame, text="All", variable=self.star_rating_var, value=0, command=self.scrape_books)
        self.radio_button_all.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        star_ratings = ["One", "Two", "Three", "Four", "Five"]
        for i, star in enumerate(star_ratings, start=2):
            radio_button = Radiobutton(self.star_rating_frame, text=f"{star} stars", variable=self.star_rating_var, value=i, command=self.scrape_books)
            radio_button.grid(row=i, column=0, sticky="w", padx=5, pady=5)

        self.books_treeview = ttk.Treeview(self.master, columns=("Title", "Price", "Star Rating"), show="headings")
        self.books_treeview.heading("Title", text="Title")
        self.books_treeview.heading("Price", text="Price")
        self.books_treeview.heading("Star Rating", text="Star Rating")
        self.books_treeview.column("Title", width=500)
        self.books_treeview.column("Price", width=100)
        self.books_treeview.column("Star Rating", width=100)
        self.books_treeview.grid(row=5, column=1, columnspan=2)

        self.add_to_cart_button = Button(self.master, text="Add to Cart", command=self.add_to_cart, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.add_to_cart_button.grid(row=6, column=1, columnspan=2, pady=(10, 0))

        self.cart_label = Label(self.master, text="Cart", font=("Courier", 16), bg="white", fg="black")
        self.cart_label.grid(row=7, column=1, pady=(20, 10), sticky="w")
        self.cart_listbox = Listbox(self.master, width=65, font=("Courier", 14), fg="#36013F", bg="#E9CFEC")
        self.cart_listbox.grid(row=8, column=1, columnspan=4, pady=(0, 20), sticky="w")
        self.total_price_label = Label(self.master, text="Total Price: $0.00", font=("Courier", 25), bg="white", fg="black")
        self.total_price_label.grid(row=8, column=1, columnspan=3, pady=(0, 20), sticky="ne")

        self.checkout_button = Button(self.master, text="Checkout", command=self.open_checkout_window, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.checkout_button.grid(row=8, column=2, pady=(0, 20), padx=(10, 0), sticky="swe")

        self.delete_button = Button(self.master, text="Delete", command=self.delete_from_cart, font=("Courier", 14), bg="white", fg="black", relief="raised")
        self.delete_button.grid(row=8, column=2, pady=(0, 20), padx=(10, 0), sticky="we")

        self.create_menu()

    def open_checkout_window(self):
        if self.cart_listbox.size() == 0:
            messagebox.showerror("Error", "Your cart is empty.")
            return
        cart_items = self.cart_listbox.get(0, tk.END)
        total_price = sum(float(item.split(" - $")[1]) for item in cart_items)
        checkout_window = Toplevel(self.master)
        checkout_view = CheckoutWindow(checkout_window, cart_items, total_price)

    def delete_from_cart(self):
        selected_index = self.cart_listbox.curselection()
        if selected_index:
            self.cart_listbox.delete(selected_index)
            self.calculate_total_price()
            messagebox.showinfo("Success", "Book deleted from cart.")
        else:
            messagebox.showerror("Error", "Please select a book to delete from the cart.")

    def create_menu(self):
        menubar = Menu(self.master)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export to Excel", command=self.export_to_excel)
        menubar.add_cascade(label="File", menu=file_menu)

        about_menu = Menu(menubar, tearoff=0)
        about_menu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="About", menu=about_menu)
        self.master.config(menu=menubar)

    def get_topics(self):
        self.categories = get_categories(self.textbox_url.get("1.0", "end-1c"))
        if self.categories:
            self.topics_listbox.delete(0, tk.END)
            for category in self.categories:
                self.topics_listbox.insert(tk.END, category)
        else:
            self.show_message("Error", "Failed to retrieve categories.")

    def scrape_books(self):
        selected_topic_indices = self.topics_listbox.curselection()
        if selected_topic_indices:
            for index in selected_topic_indices:
                selected_topic = self.topics_listbox.get(index)
                if selected_topic in self.categories:
                    books = get_books(self.categories[selected_topic])
                    if books:
                        price_range = self.price_range_var.get()
                        star_rating_filter = self.star_rating_var.get()
                        self.display_books(books, price_range, star_rating_filter)
                    else:
                        self.show_message("Error", f"No books found in the '{selected_topic}' category.")
                else:
                    self.show_message("Error", "Invalid topic selected.")
        else:
            self.show_message("Error", "No topic selected.")

    def display_books(self, books, price_range, star_rating_filter):
        star_rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        self.books_treeview.delete(*self.books_treeview.get_children())
        for book in books:
            title = book["title"]
            price = f"${book['price_usd']:.2f}"
            star_rating = star_rating_map.get(book["star_rating"], 0)

            if price_range == 1 and book["price_usd"] > 10:
                continue
            elif price_range == 2 and not (10 < book["price_usd"] <= 20):
                continue
            elif price_range == 3 and book["price_usd"] <= 20:
                continue
            if star_rating_filter != 0 and star_rating != star_rating_filter:
                continue
            self.books_treeview.insert("", "end", values=(title, price, star_rating))

    def add_to_cart(self):
        selected_book = self.books_treeview.selection()
        if selected_book:
            item = self.books_treeview.item(selected_book)
            title = item["values"][0]
            price = float(item["values"][1].replace("$", ""))
            self.cart_listbox.insert(tk.END, f"{title} - ${price:.2f}")
            self.calculate_total_price()
            messagebox.showinfo("Success", f"{title} added to cart.")
        else:
            messagebox.showerror("Error", "Please select a book to add to the cart.")

    def calculate_total_price(self):
        total_price = sum(float(item.split(" - $")[1]) for item in self.cart_listbox.get(0, tk.END))
        self.total_price_label.config(text=f"Total Price: ${total_price:.2f}")

    def export_to_excel(self):
        if not self.books_treeview.get_children():
            self.show_message("Error", "No data to export.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            data = []
            for child in self.books_treeview.get_children():
                values = self.books_treeview.item(child, "values")
                data.append(values)
            df = pd.DataFrame(data, columns=["Title", " Price", "Star Rating"])
            df.to_excel(file_path, index=False)
            self.show_message("Success", "Data exported to Excel successfully.")
        else:
            self.show_message("Error", "File save canceled.")

    def about(self):
        messagebox.showinfo("About", "This is a Book Scraper GUI.")

    def show_message(self, title, message):
        messagebox.showerror(title, message)

    def get_exchange_rate(self):
        exchange_rate = get_exchange_rate()
        if exchange_rate is not None:
            self.label_exchange_rate.config(text=f"{exchange_rate}")
        else:
            self.label_exchange_rate.config(text="Failed to retrieve exchange rate.")

def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
