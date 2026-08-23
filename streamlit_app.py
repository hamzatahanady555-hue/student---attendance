import streamlit as st

# إعدادات الصفحة والعنوان
st.set_page_config(page_title="نظام الحضور التلقائي", layout="centered")
st.title("📝 نظام تسجيل الطلاب وتوليد الأكواد بالتسلسل")

# إنشاء قاعدة بيانات مؤقتة وجعداد للأكواد المتسلسلة داخل الجلسة
if "students_database" not in st.session_state:
    st.session_state.students_database = {}
if "next_code" not in st.session_state:
    st.session_state.next_code = 5642  # البداية من كود رقم 1020 الذي حددته

# تقسيم الواجهة إلى تبويبين (TABS)
tab1, tab2 = st.tabs(["📋 تسجيل طالب جديد", "⏱️ تسجيل حضور الحصة"])

with tab1:
    st.subheader("إدخال بيانات الطالب (توليد كود تلقائي)")
    name = st.text_input("اسم الطالب")
    phone = st.text_input("رقم تليفون الطالب")
    father_phone = st.text_input("رقم تليفون الأب")
    
    # عرض الكود القادم الذي سيحصل عليه الطالب تلقائياً
    current_assigned_code = str(st.session_state.next_code)
    st.info(f"💡 الطالب القادم سيحصل تلقائياً على كود رقم: {current_assigned_code}")
    
    if st.button("تسجيل الطالب وتوليد الكود"):
        if not name:
            st.error("❌ يرجى إدخال اسم الطالب أولاً!")
        else:
            # حفظ الطالب بالكود الرقمي المتسلسل الحالي
            st.session_state.students_database[current_assigned_code] = {
                "اسم الطالب": name,
                "رقم تليفون الطالب": phone,
                "رقم تليفون الأب": father_phone,
                "حالة الحضور": "غائب"
            }
            st.success(f"✅ تم تسجيل الطالب: {name} بنجاح! كود الطالب هو: {current_assigned_code}")
            
            # زيادة العداد بمقدار 1 للطالب التالي وراءه مباشرة ليصبح 5643، 5644...
            st.session_state.next_code += 1
            st.rerun()

with tab2:
    st.subheader("التحقق من كود الطالب اليومي")
    code_input = st.text_input("ادخل كود الطالب الرقمي")
    
    if st.button("التحقق وتسجيل الحضور"):
        if code_input in st.session_state.students_database:
            st.session_state.students_database[code_input]["حالة الحضور"] = "حاضر"
            student_name = st.session_state.students_database[code_input]["اسم الطالب"]
            st.success(f"🟢 تم التحقق! الطالب [{student_name}] سُجِل حضور الآن بنجاح.")
        else:
            st.error("❌ هذا الكود غير مسجل في النظام! تأكد من الرقم.")
