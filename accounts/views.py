from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages

from reportlab.pdfgen import canvas

from invoices.models import Invoice, InvoiceItem, Product


# ----------------------
# HOME
# ----------------------
def home(request):
    return render(request, "home.html")


# ----------------------
# REGISTER
# ----------------------
def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Username and password required")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "register.html")


# ----------------------
# LOGIN
# ----------------------
def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid username or password"

    return render(request, "login.html", {"error": error})


# ----------------------
# LOGOUT
# ----------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


# ----------------------
# DASHBOARD
# ----------------------
@login_required
def dashboard(request):

    invoices = Invoice.objects.filter(owner=request.user).order_by("-id")[:5]

    total = sum(i.total or 0 for i in Invoice.objects.filter(owner=request.user))

    return render(request, "dashboard.html", {
        "invoices": invoices,
        "invoice_count": invoices.count(),
        "total_revenue": total
    })


# ----------------------
# PRODUCTS
# ----------------------
@login_required
def products(request):

    items = Product.objects.filter(owner=request.user)

    return render(request, "products.html", {
        "products": items
    })


@login_required
def add_product(request):

    if request.method == "POST":

        Product.objects.create(
            owner=request.user,
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            stock=request.POST.get("stock")
        )

        return redirect("products")

    return render(request, "add_product.html")


# ----------------------
# CREATE INVOICE (POS + DISCOUNT READY)
# ----------------------
@login_required
def create_invoice(request):

    products = Product.objects.filter(owner=request.user)

    if request.method == "POST":

        invoice = Invoice.objects.create(
            owner=request.user,
            invoice_number="TEMP",
            customer_name=request.POST.get("customer_name"),
            customer_phone=request.POST.get("customer_phone"),
            discount=request.POST.get("discount") or 0
        )

        product_ids = request.POST.getlist("product_id[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        for pid, qty, price in zip(product_ids, quantities, prices):

            if pid:
                product = get_object_or_404(Product, id=pid, owner=request.user)

                qty = int(qty)

                if product.stock < qty:
                    messages.error(request, f"Not enough stock for {product.name}")
                    continue

                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=product.name,
                    quantity=qty,
                    price=float(price)
                )

                product.stock -= qty
                product.save()

        invoice.update_total()

        invoice.invoice_number = f"INV-{invoice.id:05d}"
        invoice.save()

        return redirect("dashboard")

    return render(request, "create_invoice.html", {
        "products": products
    })


# ----------------------
# INVOICE DETAIL
# ----------------------
@login_required
def invoice_detail(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id,
        owner=request.user
    )

    return render(request, "invoice_detail.html", {
        "invoice": invoice
    })


# ----------------------
# EDIT INVOICE (FIXED + DISCOUNT SUPPORT)
# ----------------------
@login_required
def edit_invoice(request, invoice_id):

    invoice = get_object_or_404(
        Invoice,
        id=invoice_id,
        owner=request.user
    )

    if request.method == "POST":

        invoice.customer_name = request.POST.get("customer_name")
        invoice.customer_phone = request.POST.get("customer_phone")

        # discount update
        invoice.discount = request.POST.get("discount") or 0

        invoice.save()

        item_ids = request.POST.getlist("item_id[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        for i in range(len(item_ids)):

            try:
                item = InvoiceItem.objects.get(
                    id=item_ids[i],
                    invoice=invoice
                )

                item.quantity = int(quantities[i])
                item.price = float(prices[i])
                item.save()

            except:
                continue

        invoice.update_total()

        return redirect("invoice_detail", invoice_id=invoice.id)

    return render(request, "edit_invoice.html", {
        "invoice": invoice
    })


# ----------------------
# DELETE INVOICE
# ----------------------
@login_required
def delete_invoice(request, invoice_id):

    invoice = get_object_or_404(Invoice, id=invoice_id, owner=request.user)

    if request.method == "POST":
        invoice.delete()
        return redirect("dashboard")

    return render(request, "delete_invoice.html", {
        "invoice": invoice
    })


# ----------------------
# ANALYTICS
# ----------------------
@login_required
def analytics(request):

    invoices = Invoice.objects.filter(owner=request.user)

    total = sum(i.total or 0 for i in invoices)

    return render(request, "analytics.html", {
        "total_revenue": total,
        "total_invoices": invoices.count(),
        "average_invoice": total / invoices.count() if invoices.count() else 0
    })