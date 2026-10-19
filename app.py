import streamlit as st
import pandas as pd
from datetime import datetime
import random
import os

# ---------------------------------------------------------
# TRÀ SỮA CỦA PMINH - MINI E-COMMERCE DEMO
# Chạy bằng: streamlit run app.py
# ---------------------------------------------------------

st.set_page_config(
    page_title="Trà sữa của Pminh",
    page_icon="🧋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Giao diện
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #fff8f2 0%, #fff0f5 100%); }
    h1, h2, h3 { color: #6b3f36; }
    div[data-testid="stMetric"] {
        background: #ffffff; padding: 14px; border-radius: 16px;
        border: 1px solid #f2d9d0;
    }
    .hero {
        padding: 28px; border-radius: 22px; text-align: center;
        background: linear-gradient(120deg, #f7d9c4, #f6c6d8);
        color: #56352f; margin-bottom: 18px;
    }
    .small-note { color: #80665e; font-size: 0.92rem; }
</style>
""", unsafe_allow_html=True)

MENU = {
    "Pminh Signature 🧋": {"price": 39000, "desc": "Trà sữa nhà làm, kem sữa mịn và trân châu đen.", "tag": "BÁN CHẠY"},
    "Matcha Mây Hồng 🍵": {"price": 42000, "desc": "Matcha thơm dịu, lớp kem dâu bồng bềnh.", "tag": "ĐỘC QUYỀN"},
    "Ô Long Nhãn Vàng 🍯": {"price": 38000, "desc": "Ô long rang nhẹ kết hợp vị ngọt thanh của nhãn.", "tag": "THANH MÁT"},
    "Dâu Sữa Mộng Mơ 🍓": {"price": 37000, "desc": "Dâu chua ngọt, sữa tươi và thạch dâu.", "tag": "ĐƯỢC YÊU THÍCH"},
    "Trà Đào Cam Sả 🍑": {"price": 35000, "desc": "Trà trái cây thơm mát, có cam và sả.", "tag": "ÍT BÉO"},
    "Cacao Đêm Muộn 🍫": {"price": 40000, "desc": "Cacao đậm vị, dành cho hội mê chocolate.", "tag": "ĐẬM VỊ"},
    "Trà Sữa Khoai Môn 💜": {"price": 38000, "desc": "Khoai môn bùi béo với màu tím nhẹ nhàng.", "tag": "MỚI"},
    "Trà Chanh Nhiệt Đới 🍋": {"price": 32000, "desc": "Chanh tươi và trà thanh nhẹ.", "tag": "GIẢI NHIỆT"},
}

SIZES = {"S": 0, "M": 5000, "L": 10000}
TOPPINGS = {
    "Trân châu đen": 5000, "Trân châu trắng": 6000, "Thạch trái cây": 5000,
    "Pudding trứng": 7000, "Kem cheese": 9000, "Thạch củ năng": 6000,
    "Không thêm topping": 0
}
SUGAR = ["100%", "70%", "50%", "30%", "0%"]
ICE = ["100% đá", "70% đá", "50% đá", "30% đá", "Không đá"]

if "cart" not in st.session_state:
    st.session_state.cart = []
if "paid_order" not in st.session_state:
    st.session_state.paid_order = None
if "orders_count" not in st.session_state:
    st.session_state.orders_count = 0
if "points" not in st.session_state:
    st.session_state.points = 0

def money(value):
    return f"{int(value):,}".replace(",", ".") + " đ"

def create_invoice(customer, items, subtotal, discount, delivery_fee, total, payment, note):
    lines = [
        "=" * 48, "TRÀ SỮA CỦA PMINH - HÓA ĐƠN", "=" * 48,
        f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"Khách hàng: {customer or 'Khách vãng lai'}",
        f"Thanh toán: {payment}",
        f"Ghi chú: {note or 'Không có'}", "-" * 48
    ]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['Món']} - Size {item['Size']} x{item['SL']}")
        lines.append(f"   Đường: {item['Đường']} | Đá: {item['Đá']}")
        lines.append(f"   Topping: {item['Topping']}")
        lines.append(f"   {money(item['Đơn giá'])} x {item['SL']} = {money(item['Thành tiền'])}")
    lines += [
        "-" * 48, f"Tạm tính: {money(subtotal)}",
        f"Giảm giá: -{money(discount)}", f"Phí giao hàng: {money(delivery_fee)}",
        f"TỔNG THANH TOÁN: {money(total)}", "=" * 48,
        "Cảm ơn bạn đã chọn Trà sữa của Pminh! 💗"
    ]
    return "\n".join(lines)

# Header
st.markdown("""
<div class="hero">
  <h1>🧋 Trà sữa của Pminh</h1>
  <p>Nhấp một ngụm vui — chọn đúng gu, chill đúng điệu!</p>
  <p>✨ Pha theo mood của bạn • Topping tùy gu • Ngọt theo ý thích ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar: tính năng khám phá
with st.sidebar:
    st.image("TRASUA.jpg", use_container_width=True) if os.path.exists("TRASUA.jpg") else st.markdown("## 🧋 Pminh Tea")
    st.markdown("### 🌈 Trạm chọn mood")
    mood = st.selectbox("Hôm nay bạn đang cảm thấy...", [
        "Vui vẻ, cần chút bùng nổ", "Mệt mỏi, muốn dịu dàng",
        "Tập trung học bài", "Muốn refresh bản thân", "Không biết uống gì!"
    ])
    mood_recs = {
        "Vui vẻ, cần chút bùng nổ": "Cacao Đêm Muộn 🍫",
        "Mệt mỏi, muốn dịu dàng": "Trà Sữa Khoai Môn 💜",
        "Tập trung học bài": "Ô Long Nhãn Vàng 🍯",
        "Muốn refresh bản thân": "Trà Đào Cam Sả 🍑",
        "Không biết uống gì!": "Pminh Signature 🧋"
    }
    st.success(f"💡 Gợi ý dành cho bạn: **{mood_recs[mood]}**")
    st.caption("Gợi ý vui để chọn món, không phải tư vấn sức khỏe.")
    st.markdown("---")
    st.markdown("### 🎟️ Mã ưu đãi")
    coupon = st.selectbox("Chọn mã giảm giá", ["Không dùng mã", "PMINH10 - giảm 10%", "HELLO - giảm 5%", "FREESHIP - miễn phí giao hàng"])
    st.markdown("---")
    st.markdown("### 💗 Điểm Pminh")
    st.metric("Điểm tích lũy hiện có", st.session_state.points)
    st.caption("Demo: đơn đã xác nhận được cộng 1 điểm cho mỗi 10.000đ thanh toán.")

tab_menu, tab_order, tab_rewards = st.tabs(["🍹 Khám phá menu", "🛍️ Đặt món & giỏ hàng", "🎁 Góc Pminh Club"])

with tab_menu:
    st.subheader("Menu nhà Pminh")
    search = st.text_input("🔎 Tìm món bạn thích", placeholder="Ví dụ: matcha, dâu, ô long...")
    categories = st.multiselect("Lọc theo phong cách", ["Bán chạy", "Trái cây", "Béo thơm", "Mới lạ"], default=[])
    category_map = {
        "Pminh Signature 🧋": ["Bán chạy", "Béo thơm"],
        "Matcha Mây Hồng 🍵": ["Béo thơm", "Mới lạ"],
        "Ô Long Nhãn Vàng 🍯": ["Trái cây"],
        "Dâu Sữa Mộng Mơ 🍓": ["Trái cây", "Béo thơm"],
        "Trà Đào Cam Sả 🍑": ["Trái cây"],
        "Cacao Đêm Muộn 🍫": ["Béo thơm"],
        "Trà Sữa Khoai Môn 💜": ["Béo thơm", "Mới lạ"],
        "Trà Chanh Nhiệt Đới 🍋": ["Trái cây"],
    }
    visible = []
    for name, item in MENU.items():
        if search.lower() in name.lower() or search.lower() in item["desc"].lower():
            if not categories or any(c in category_map[name] for c in categories):
                visible.append((name, item))
    if not visible:
        st.info("Chưa tìm thấy món phù hợp. Thử một từ khóa khác nhé!")
    else:
        cols = st.columns(2)
        for idx, (name, item) in enumerate(visible):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### {name}")
                    st.caption(f"✨ {item['tag']}")
                    st.write(item["desc"])
                    st.markdown(f"**{money(item['price'])}**")
                    if st.button(f"Chọn món: {name}", key=f"menu_{name}", use_container_width=True):
                        st.session_state.quick_pick = name
                        st.toast(f"Đã chọn {name}! Sang tab Đặt món để tùy chỉnh nha.")
    if "quick_pick" in st.session_state:
        st.info(f"🧋 Món bạn vừa chọn: **{st.session_state.quick_pick}**. Bạn có thể tùy chỉnh trong tab Đặt món.")

with tab_order:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("📝 Tùy chỉnh ly trà sữa")
        customer = st.text_input("Tên người đặt", placeholder="Pminh")
        default_drink = st.session_state.get("quick_pick", list(MENU.keys())[0])
        drink_list = list(MENU.keys())
        default_index = drink_list.index(default_drink) if default_drink in drink_list else 0
        drink = st.selectbox("Chọn món", drink_list, index=default_index)
        size = st.radio("Kích cỡ", list(SIZES.keys()), horizontal=True, help="Size M +5.000đ, size L +10.000đ")
        topping_choices = st.multiselect("Topping (có thể chọn nhiều)", list(TOPPINGS.keys()), default=["Trân châu đen"])
        sugar = st.select_slider("Mức đường", options=SUGAR, value="50%")
        ice = st.select_slider("Mức đá", options=ICE, value="70% đá")
        quantity = st.number_input("Số lượng ly", min_value=1, max_value=30, value=1, step=1)
        note = st.text_input("Ghi chú cho quán", placeholder="Ví dụ: để riêng topping, ghi lời nhắn...")
        eco = st.checkbox("🌱 Không lấy ống hút/ muỗng nhựa (thân thiện môi trường)")
        unit = MENU[drink]["price"] + SIZES[size] + sum(TOPPINGS[t] for t in topping_choices)
        if len(topping_choices) == 0:
            topping_text = "Không"
        else:
            topping_text = ", ".join(t for t in topping_choices if t != "Không thêm topping") or "Không"
        st.info(f"Giá mỗi ly: **{money(unit)}**  ·  Thành tiền: **{money(unit * quantity)}**")
        if st.button("➕ Thêm vào giỏ hàng", type="primary", use_container_width=True):
            st.session_state.cart.append({
                "Món": drink, "Size": size, "Đường": sugar, "Đá": ice,
                "Topping": topping_text, "SL": int(quantity), "Đơn giá": unit,
                "Thành tiền": unit * int(quantity), "Ghi chú": note,
                "Bao bì xanh": "Có" if eco else "Không"
            })
            st.session_state.paid_order = None
            st.toast("Đã thêm món vào giỏ hàng 🧋", icon="✅")
            st.rerun()

    with right:
        st.subheader("🛒 Giỏ hàng của bạn")
        if not st.session_state.cart:
            st.info("Giỏ hàng còn trống. Chọn một món thật ngon nha!")
        else:
            df = pd.DataFrame(st.session_state.cart)
            st.dataframe(df[["Món", "Size", "Topping", "SL", "Đơn giá", "Thành tiền"]], hide_index=True, use_container_width=True)
            subtotal = int(df["Thành tiền"].sum())
            if coupon.startswith("PMINH10"):
                discount_rate = 0.10
            elif coupon.startswith("HELLO"):
                discount_rate = 0.05
            else:
                discount_rate = 0
            discount = int(subtotal * discount_rate)
            delivery_fee = 0 if subtotal >= 100000 or coupon.startswith("FREESHIP") else 15000
            total = subtotal - discount + delivery_fee
            a, b = st.columns(2)
            a.metric("Tạm tính", money(subtotal))
            b.metric("Giảm giá", money(discount))
            st.write(f"🚚 Phí giao hàng: **{money(delivery_fee)}**" + (" (miễn phí)" if delivery_fee == 0 else ""))
            st.markdown(f"## Tổng thanh toán: {money(total)}")
            payment = st.radio("Phương thức thanh toán", ["Tiền mặt khi nhận hàng", "Chuyển khoản (demo)", "Ví điện tử (demo)"])
            address = st.text_input("Địa chỉ nhận hàng", placeholder="Nhập địa chỉ giao hàng (nếu cần)")
            if st.button("🗑️ Xóa toàn bộ giỏ", use_container_width=True):
                st.session_state.cart = []
                st.session_state.paid_order = None
                st.rerun()
            if st.button("💗 Xác nhận đặt hàng", type="primary", use_container_width=True):
                if not customer.strip():
                    st.warning("Bạn nhập tên người đặt trước nha.")
                elif not address.strip():
                    st.warning("Bạn nhập địa chỉ nhận hàng để hoàn tất đơn demo nhé.")
                else:
                    st.session_state.paid_order = {
                        "customer": customer, "items": st.session_state.cart.copy(),
                        "subtotal": subtotal, "discount": discount,
                        "delivery_fee": delivery_fee, "total": total,
                        "payment": payment, "note": " | ".join([x["Ghi chú"] for x in st.session_state.cart if x["Ghi chú"]]) or "Không có",
                        "address": address
                    }
                    st.session_state.orders_count += 1
                    st.session_state.points += total // 10000
                    st.balloons()
                    st.success("Đặt hàng thành công! Đây là bản demo, chưa thu tiền hoặc gửi đơn đến cửa hàng.")
        if st.session_state.paid_order:
            order = st.session_state.paid_order
            st.markdown("---")
            st.subheader("🧾 Xác nhận đơn hàng")
            st.success(f"Cảm ơn {order['customer']}! Đơn của bạn đã được ghi nhận trên phiên làm việc này.")
            st.write(f"**Địa chỉ:** {order['address']}")
            st.write(f"**Thanh toán:** {order['payment']}")
            st.write(f"**Tổng cộng:** {money(order['total'])}")
            invoice = create_invoice(order["customer"], order["items"], order["subtotal"], order["discount"], order["delivery_fee"], order["total"], order["payment"], order["note"])
            st.download_button("📥 Tải hóa đơn (.txt)", data=invoice, file_name=f"HoaDon_Pminh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain", use_container_width=True)
            if st.button("🔄 Tạo đơn mới", use_container_width=True):
                st.session_state.cart = []
                st.session_state.paid_order = None
                st.rerun()

with tab_rewards:
    st.subheader("🎁 Pminh Club — mỗi ly là một niềm vui")
    c1, c2, c3 = st.columns(3)
    c1.metric("Số đơn demo đã tạo", st.session_state.orders_count)
    c2.metric("Điểm đang có", st.session_state.points)
    c3.metric("Còn thiếu đến 50 điểm", max(0, 50 - st.session_state.points))
    st.markdown("#### 🌟 Quyền lợi thành viên")
    st.markdown("""
    - **10 điểm:** mở khóa một lời chúc bí mật từ Pminh.
    - **25 điểm:** gợi ý một combo đồ uống theo mood.
    - **50 điểm:** nhận mã ưu đãi 15% trong bản demo.
    """)
    if st.session_state.points >= 50:
        st.success("🎉 Bạn đã mở khóa mã PCLUB15 (demo).")
        st.code("PCLUB15")
    elif st.session_state.points >= 25:
        st.success("🎁 Bạn đã mở khóa gợi ý combo đặc biệt!")
        st.write("Combo chill: Ô Long Nhãn Vàng + Dâu Sữa Mộng Mơ.")
    elif st.session_state.points >= 10:
        messages = [
            "Bạn xứng đáng có một ngày dịu dàng hơn. 💗",
            "Chậm lại một chút, nhấp một ngụm ngon và tiếp tục nhé. 🌷",
            "Gu của bạn là độc nhất — cứ là chính mình nha. ✨"
        ]
        st.success("💌 Lời nhắn bí mật dành cho bạn:")
        st.write(random.choice(messages))
    else:
        st.info("Đặt món trong tab bên cạnh để tích điểm và mở khóa quà nhé!")

st.markdown("---")
st.markdown("<p class='small-note' style='text-align:center'>Trà sữa của Pminh © 2026 · Giao diện demo phục vụ học tập. Đơn hàng, mã giảm giá và tích điểm chưa kết nối hệ thống thanh toán thật.</p>", unsafe_allow_html=True)
