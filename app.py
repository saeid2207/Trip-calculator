import math
import streamlit as st

st.set_page_config(page_title="حساب دنگ سفر", page_icon="🧾", layout="centered")

st.title("🧾 حساب دنگ سفر")
st.caption("افراد و گروه‌ها رو وارد کن، هزینه‌ها رو ثبت کن، تسویه رو ببین.")

# ---------- مقداردهی اولیه ----------
if "people" not in st.session_state:
    st.session_state.people = ["سعید", "حسین", "سبحان"]
if "groups" not in st.session_state:
    st.session_state.groups = {}
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "expense_titles" not in st.session_state:
    st.session_state.expense_titles = [
        "رستوران", "بنزین", "تنقلات", "خرید", "بلیط",
        "اقامت", "حمل و نقل", "تفریح", "ورودی", "شهریه", "سایر",
    ]
if "form_counter" not in st.session_state:
    st.session_state.form_counter = 0

# ---------- بخش ۱: افراد ----------
st.header("۱) افراد")
names_input = st.text_input(
    "اسم افراد (با ویرگول «،» جدا کن)",
    value="، ".join(st.session_state.people),
    key="names_input",
)
if st.button("💾 ذخیره افراد"):
    raw = st.session_state.names_input.replace(",", "،")
    people = [n.strip() for n in raw.split("،") if n.strip()]
    if len(people) < 2:
        st.error("حداقل ۲ نفر لازمه.")
    else:
        st.session_state.people = people
        st.session_state.groups = {
            g: [m for m in members if m in people]
            for g, members in st.session_state.groups.items()
        }
        st.session_state.expenses = []
        st.success("✅ ذخیره شد.")
        st.rerun()

people = st.session_state.people

# ---------- بخش ۲: گروه‌ها ----------
st.header("۲) گروه‌بندی (اختیاری)")
st.caption("اگه چند نفر با هم یه خانواده/گروه هستن، اینجا گروهشون کن. "
           "هر کسی تو گروهی نباشه، تنها حساب می‌شه.")

grouped_people = set(m for members in st.session_state.groups.values() for m in members)
available_people = [p for p in people if p not in grouped_people]

with st.form("add_group", clear_on_submit=True):
    group_name = st.text_input("اسم گروه", placeholder="مثلاً خانواده سعید")
    members = st.multiselect("اعضای گروه", available_people)
    if st.form_submit_button("➕ افزودن گروه"):
        if not group_name.strip():
            st.error("اسم گروه رو وارد کن.")
        elif len(members) < 1:
            st.error("حداقل یه عضو انتخاب کن.")
        else:
            st.session_state.groups[group_name.strip()] = members
            st.success(f"✅ گروه «{group_name}» ساخته شد.")
            st.rerun()

if st.session_state.groups:
    st.markdown("**گروه‌های فعلی:**")
    for g, members in list(st.session_state.groups.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"👥 **{g}**: {', '.join(members)}")
        with col2:
            if st.button("🗑️", key=f"del_group_{g}"):
                del st.session_state.groups[g]
                st.rerun()
else:
    st.info("هنوز گروهی ساخته نشده. همه افراد تنها حساب می‌شن.")

# ---------- محاسبه واحدها ----------
units = {}
for g, members in st.session_state.groups.items():
    units[g] = len(members)
for p in people:
    if p not in grouped_people:
        units[p] = 1

# ---------- ویرایش عناوین ----------
with st.expander("✏️ ویرایش لیست عناوین هزینه"):
    titles_input = st.text_area(
        "هر عنوان توی یه خط",
        value="\n".join(st.session_state.expense_titles),
        height=200,
        key="titles_edit",
    )
    if st.button("💾 ذخیره عناوین"):
        new_titles = [t.strip() for t in titles_input.split("\n") if t.strip()]
        if len(new_titles) < 1:
            st.error("حداقل یه عنوان لازمه.")
        else:
            st.session_state.expense_titles = new_titles
            st.success("✅ عناوین ذخیره شد.")
            st.rerun()
    if st.button("🔄 بازگشت به پیش‌فرض"):
        st.session_state.expense_titles = [
            "رستوران", "بنزین", "تنقلات", "خرید", "بلیط",
            "اقامت", "حمل و نقل", "تفریح", "ورودی", "شهریه", "سایر",
        ]
        st.rerun()

# ---------- بخش ۳: افزودن هزینه ----------
st.header("۳) افزودن هزینه")

# کلیدهای پویا برای خالی شدن فرم
fc = st.session_state.form_counter

col1, col2 = st.columns(2)
with col1:
    title_choice = st.selectbox(
        "عنوان هزینه",
        st.session_state.expense_titles,
        key=f"title_choice_{fc}",
    )
with col2:
    custom_title = st.text_input("یا عنوان دلخواه", key=f"custom_title_{fc}")

unit_names = list(units.keys())
payer_unit = st.selectbox(
    "پرداخت‌کننده (گروه یا فرد)", unit_names, key=f"payer_unit_{fc}"
)

amount = st.number_input(
    "مبلغ کل فاکتور (تومن)",
    min_value=0,
    step=10000,
    value=None,
    format="%d",
    key=f"amount_{fc}",
)

vat_amount = st.number_input(
    "مبلغ ارزش افزوده (تومن)",
    min_value=0,
    step=1000,
    value=None,
    format="%d",
    key=f"vat_amount_{fc}",
)

st.markdown("**نحوه تقسیم:**")
split_mode = st.radio(
    "نحوه تقسیم",
    ["بر اساس تعداد نفرات", "دستی (سهم هر واحد از قیمت پایه)"],
    horizontal=False,
    label_visibility="collapsed",
    key=f"split_mode_{fc}",
)

selected_units = {}
manual_shares = {}

if split_mode == "بر اساس تعداد نفرات":
    st.caption("تیک بزن، بعد تعداد مصرف‌کننده از هر واحد رو مشخص کن.")
    for unit_name in units.keys():
        col1, col2 = st.columns([3, 1])
        with col1:
            checked = st.checkbox(unit_name, key=f"unit_{unit_name}_{fc}")
        with col2:
            if checked:
                count = st.number_input(
                    "تعداد",
                    min_value=1,
                    max_value=units[unit_name],
                    value=units[unit_name],
                    step=1,
                    key=f"count_{unit_name}_{fc}",
                    label_visibility="collapsed",
                )
            else:
                count = 0
        if checked:
            selected_units[unit_name] = count
else:
    st.caption(
        "سهم هر واحد رو از **قیمت پایه** (بدون ارزش افزوده) وارد کن. "
        "این عدد رو از فاکتور بردار."
    )
    for unit_name in units.keys():
        manual_shares[unit_name] = st.number_input(
            f"سهم {unit_name}",
            min_value=0,
            step=10000,
            value=None,
            format="%d",
            key=f"manual_{unit_name}_{fc}",
        )

# --- دکمه افزودن ---
if st.button("➕ افزودن هزینه"):
    title = custom_title.strip() or title_choice

    if amount is None or amount <= 0:
        st.error("مبلغ فاکتور رو وارد کن.")
        st.stop()
    if vat_amount is None:
        vat_amount = 0

    if split_mode == "بر اساس تعداد نفرات":
        if not selected_units:
            st.error("حداقل یه واحد مصرف‌کننده انتخاب کن.")
            st.stop()
        total_consumers = sum(selected_units.values())
        base_share = {
            u: amount * cnt / total_consumers
            for u, cnt in selected_units.items()
        }
    else:
        base_share = {
            u: v for u, v in manual_shares.items() if v and v > 0
        }
        sum_base = sum(base_share.values())
        if sum_base == 0:
            st.error("حداقل سهم یه واحد رو وارد کن.")
            st.stop()

    sum_base = sum(base_share.values())
    if sum_base <= 0:
        st.error("جمع سهم‌ها صفره.")
        st.stop()

    factor = amount / sum_base
    final_share = {u: v * factor for u, v in base_share.items()}

    st.session_state.expenses.append(
        {
            "title": title,
            "payer_unit": payer_unit,
            "amount": amount,
            "vat_amount": vat_amount,
            "mode": split_mode,
            "base_share": base_share,
            "final_share": final_share,
        }
    )
    # افزایش شمارنده برای خالی شدن فرم
    st.session_state.form_counter += 1
    st.success("✅ هزینه ثبت شد.")
    st.rerun()

# ---------- بخش ۴: لیست هزینه‌ها ----------
st.header("۴) لیست هزینه‌ها")
if not st.session_state.expenses:
    st.info("هنوز هزینه‌ای ثبت نشده.")
else:
    for i, exp in enumerate(st.session_state.expenses):
        vat_text = (
            f" | ارزش افزوده: {exp['vat_amount']:,.0f} تومن"
            if exp.get("vat_amount", 0) > 0
            else ""
        )
        with st.expander(
            f"{exp['title']} — {exp['amount']:,} تومن "
            f"(پرداخت: {exp['payer_unit']}){vat_text}"
        ):
            st.write("سهم پایه هر واحد (بدون ارزش افزوده):")
            for u, s in exp["base_share"].items():
                st.write(f"- {u}: {s:,.0f}")
            st.write("**سهم نهایی (با ارزش افزوده):**")
            total_final = 0
            for u, s in exp["final_share"].items():
                st.write(f"- {u}: {s:,.0f}")
                total_final += s
            st.write(f"**جمع نهایی: {total_final:,.0f} تومن**")
            if st.button("🗑️ حذف", key=f"del_{i}"):
                st.session_state.expenses.pop(i)
                st.rerun()

    if st.button("🧹 پاک کردن همه هزینه‌ها"):
        st.session_state.expenses = []
        st.rerun()

# ---------- بخش ۵: جدول ماتریسی ----------
st.header("۵) جدول ماتریسی هزینه‌ها")

if not st.session_state.expenses:
    st.info("هنوز هزینه‌ای ثبت نشده.")
else:
    unit_list = list(units.keys())

    # سربرگ جدول
    header = "| مورد | " + " | ".join(unit_list) + " |"
    separator = "|---|" + "|".join(["---"] * len(unit_list)) + "|"

    rows = []
    # جمع ستون‌ها
    col_totals = {u: 0.0 for u in unit_list}

    for exp in st.session_state.expenses:
        row_cells = []
        for u in unit_list:
            val = exp["final_share"].get(u, 0)
            col_totals[u] += val
            row_cells.append(f"{val:,.0f}" if val > 0 else "۰")
        rows.append(f"| {exp['title']} | " + " | ".join(row_cells) + " |")

    # ردیف جمع
    total_row = "| **جمع** | " + " | ".join(
        f"**{col_totals[u]:,.0f}**" for u in unit_list
    ) + " |"
    rows.append(total_row)

    table_md = header + "\n" + separator + "\n" + "\n".join(rows)
    st.markdown(table_md)

    # جمع کل
    grand_total = sum(col_totals.values())
    st.write(f"**جمع کل:** {grand_total:,.0f} تومن")

# ---------- بخش ۶: تسویه ----------
st.header("۶) تسویه نهایی")
if st.session_state.expenses and st.button("💸 محاسبه کن"):
    unit_paid = {u: 0.0 for u in units}
    unit_share_total = {u: 0.0 for u in units}

    for exp in st.session_state.expenses:
        unit_paid[exp["payer_unit"]] += exp["amount"]
        for u, share in exp["final_share"].items():
            unit_share_total[u] += share

    unit_balance = {u: unit_paid[u] - unit_share_total[u] for u in units}

    st.subheader("📊 خلاصه (بر اساس واحد)")
    for u in units:
        st.write(
            f"**{u}** — پرداخت: {unit_paid[u]:,.0f} | "
            f"سهم: {unit_share_total[u]:,.0f} | "
            f"بالانس: {unit_balance[u]:+,.0f}"
        )

    debtors = [[u, -unit_balance[u]] for u in units if unit_balance[u] < -0.01]
    creditors = [[u, unit_balance[u]] for u in units if unit_balance[u] > 0.01]
    debtors.sort(key=lambda x: -x[1])
    creditors.sort(key=lambda x: -x[1])

    transactions = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt = debtors[i]
        creditor, credit = creditors[j]
        pay = min(debt, credit)
        transactions.append((debtor, creditor, pay))
        debtors[i][1] -= pay
        creditors[j][1] -= pay
        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1

    st.subheader("💰 کی به کی چقدر بده")
    if not transactions:
        st.success("همه چی صاف صافیه! 🎉")
    else:
        for debtor, creditor, amount in transactions:
            amount = math.ceil(amount)
            st.markdown(
                f"👉 **{debtor}** باید **{amount:,} تومن** به **{creditor}** بده"
            )
