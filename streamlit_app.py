import streamlit as st
import pandas as pd
from io import BytesIO

# إعدادات الصفحة والعنوان
st.set_page_config(page_title="نظام الحضور والغياب للمراحل", layout="centered")
st.title("📝 نظام إدارة حضور وغياب الطلاب حسب المرحلة الدراسية")

# إنشاء قاعدة بيانات مؤقتة وجعداد للأكواد المتسلسلة داخل الجلسة
if "students_database" not in st.session_state:
    st.session_state.students_database = {}
if "next_code" not in st.session_state:
    st.session_state.next_code = 1020  # البداية من كود رقم 1020 الذي حددته

# تقسيم الواجهة إلى ثلاثة تبويبات (TABS)
tab1, tab2, tab3 = st.tabs(["📋 تسجيل طالب جديد", "⏱️ تسجيل حضور الحصة", "📊 إحصائيات الحضور والغياب"])

with tab1:
    st.subheader("إدخال بيانات الطالب وتحديد مرحلته")
    name = st.text_input("اسم الطالب")
    
    # قائمة اختيار المرحلة الدراسية للطالب
    grade = st.selectbox("المرحلة الدراسية للطالب:", [
        "أولى إعدادي", 
        "ثانية إعدادي", 
        "ثالثة إعدادي", 
        "أولى ثانوي", 
        "ثانية ثانوي", 
        "ثالثة ثانوي"
    ])
    
    phone = st.text_input("رقم تليفون الطالب")
    father_phone = st.text_input("رقم تليفون الأب")
    
    # عرض الكود القادم الذي سيحصل عليه الطالب تلقائياً
    current_assigned_code = str(st.session_state.next_code)
    st.info(f"💡 الطالب القادم سيحصل تلقائياً على كود رقم: {current_assigned_code}")
    
    if st.button("تسجيل الطالب وتوليد الكود"):
        if not name:
            st.error("❌ يرجى إدخال اسم الطالب أولاً!")
        else:
            # حفظ الطالب بالكود الرقمي المتسلسل وتحديد مرحلته الدراسية وحالته الافتراضية "غائب"
            st.session_state.students_database[current_assigned_code] = {
                "كود الطالب": current_assigned_code,
                "اسم الطالب": name,
                "المرحلة الدراسية": grade,
                "رقم تليفون الطالب": phone,
                "رقم تليفون الأب": father_phone,
                "حالة الحضور": "غائب"
            }
            st.success(f"✅ تم تسجيل الطالب: {name} ({grade}) بنجاح! كود الطالب هو: {current_assigned_code}")
            
            # زيادة العداد بمقدار 1 للطالب التالي وراءه مباشرة
            st.session_state.next_code += 1
            st.rerun()

with tab2:
    st.subheader("التحقق من كود الطالب اليومي")
    code_input = st.text_input("ادخل كود الطالب الرقمي لتسجيل حضوره")
    
    if st.button("التحقق وتسجيل الحضور"):
        if code_input in st.session_state.students_database:
            st.session_state.students_database[code_input]["حالة الحضور"] = "حاضر"
            student_name = st.session_state.students_database[code_input]["اسم الطالب"]
            student_grade = st.session_state.students_database[code_input]["المرحلة الدراسية"]
            st.success(f"🟢 تم التحقق! الطالب [{student_name}] من مرحلة ({student_grade}) سُجِل حضور الآن.")
        else:
            st.error("❌ هذا الكود غير مسجل في النظام! تأكد من الرقم.")

with tab3:
    st.subheader("📈 كشف الحضور والغياب حسب الصف")
    
    if not st.session_state.students_database:
        st.info("💡 لا يوجد طلاب مسجلين في النظام حتى الآن.")
    else:
        # تحويل البيانات بالكامل إلى جدول منظم لسهولة الفرز والتصفية
        df_all = pd.DataFrame(st.session_state.students_database.values())
        
        # فلتر علوي للمدرس لاختيار الصف الذي يريد مراجعته لوحده
        selected_grade = st.selectbox("اختر المرحلة لعرض إحصائياتها بشكل منفصل:", [
            "الكل",
            "أولى إعدادي", 
            "ثانية إعدادي", 
            "ثالثة إعدادي", 
            "أولى ثانوي", 
            "ثانية ثانوي", 
            "ثالثة ثانوي"
        ])
        
        # تصفية الجدول بناءً على اختيار المدرس
        if selected_grade == "الكل":
            df_filtered = df_all
        else:
            df_filtered = df_all[df_all["المرحلة الدراسية"] == selected_grade]
            
        if df_filtered.empty:
            st.warning(f"⚠️ لا يوجد طلاب مسجلين في مرحلة ({selected_grade}) حتى الآن.")
        else:
            # حساب الأرقام بدقة للمرحلة المختارة فقط
            total_registered = len(df_filtered)
            total_present = len(df_filtered[df_filtered["حالة الحضور"] == "حاضر"])
            total_absent = total_registered - total_present
            
            # عرض العدادات للمرحلة المختارة
            col1, col2, col3 = st.columns(3)
            col1.metric(f"إجمالي طلاب ({selected_grade})", total_registered)
            col2.metric("🟢 عدد الحاضرين", total_present)
            col3.metric("🔴 عدد الغائبين", total_absent)
            
            st.markdown("---")
            
            # تجهيز ملف Excel للمرحلة المختارة فقط للتحميل الدائم
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name=f'كشف حضور {selected_grade}')
            processed_data = output.getvalue()
            
            # زر التحميل المنفصل
            st.download_button(
                label=f"📥 تحميل كشف غياب وحضور ({selected_grade}) بصيغة Excel",
                data=processed_data,
                file_name=f"كشف_حضور_{selected_grade}.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            st.write(f"📋 **جدول طلاب مرحلة ({selected_grade}) الحالي:**")
            # عرض جدول المرحلة المختارة فقط
            st.dataframe(df_filtered[["كود الطالب", "اسم الطالب", "المرحلة الدراسية", "حالة الحضور", "رقم تليفون الطالب"]], use_container_width=True)
