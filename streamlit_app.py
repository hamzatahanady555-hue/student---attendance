
import os; os.system("pip install xlsxwriter")
import streamlit as st
import pandas as pd
from io import BytesIO

# إعدادات الصفحة والعنوان
st.set_page_config(page_title="نظام الحضور الشامل", layout="centered")
st.title("📝 نظام إدارة حضور الطلاب والمراحل (مع الحذف والتعديل)")

# إنشاء قاعدة بيانات مؤقتة وجعداد للأكواد المتسلسلة داخل الجلسة
if "students_database" not in st.session_state:
    st.session_state.students_database = {}
if "next_code" not in st.session_state:
    st.session_state.next_code = 1020  # البداية من كود رقم 1020 الذي حددته

# تقسيم الواجهة إلى أربعة تبويبات (TABS) بعد إضافة إدارة الطلاب
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 تسجيل طالب جديد", 
    "⏱️ تسجيل حضور الحصة", 
    "📊 إحصائيات الحضور والغياب",
    "⚙️ تعديل وحذف الطلاب"
])

# قائمة المراحل الدراسية الثابتة
grades_list = ["أولى إعدادي", "ثانية إعدادي", "ثالثة إعدادي", "أولى ثانوي", "ثانية ثانوي", "ثالثة ثانوي"]

with tab1:
    st.subheader("إدخال بيانات الطالب وتحديد مرحلته")
    name = st.text_input("اسم الطالب الجديد")
    grade = st.selectbox("المرحلة الدراسية للطالب:", grades_list, key="add_grade")
    phone = st.text_input("رقم تليفون الطالب", key="add_phone")
    father_phone = st.text_input("رقم تليفون الأب", key="add_father_phone")
    
    current_assigned_code = str(st.session_state.next_code)
    st.info(f"💡 الطالب القادم سيحصل تلقائياً على كود رقم: {current_assigned_code}")
    
    if st.button("تسجيل الطالب وتوليد الكود"):
        if not name:
            st.error("❌ يرجى إدخال اسم الطالب أولاً!")
        else:
            st.session_state.students_database[current_assigned_code] = {
                "كود الطالب": current_assigned_code,
                "اسم الطالب": name,
                "المرحلة الدراسية": grade,
                "رقم تليفون الطالب": phone,
                "رقم تليفون الأب": father_phone,
                "حالة الحضور": "غائب"
            }
            st.success(f"✅ تم تسجيل الطالب: {name} ({grade}) بنجاح! كوده هو: {current_assigned_code}")
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
        df_all = pd.DataFrame(st.session_state.students_database.values())
        selected_grade = st.selectbox("اختر المرحلة لعرض إحصائياتها منفصلة:", ["الكل"] + grades_list)
        
        if selected_grade == "الكل":
            df_filtered = df_all
        else:
            df_filtered = df_all[df_all["المرحلة الدراسية"] == selected_grade]
            
        if df_filtered.empty:
            st.warning(f"⚠️ لا يوجد طلاب مسجلين في مرحلة ({selected_grade}) حتى الآن.")
        else:
            total_registered = len(df_filtered)
            total_present = len(df_filtered[df_filtered["حالة الحضور"] == "حاضر"])
            total_absent = total_registered - total_present
            
            col1, col2, col3 = st.columns(3)
            col1.metric(f"إجمالي طلاب ({selected_grade})", total_registered)
            col2.metric("🟢 عدد الحاضرين", total_present)
            col3.metric("🔴 عدد الغائبين", total_absent)
            
            st.markdown("---")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name=f'كشف {selected_grade}')
            processed_data = output.getvalue()
            
            st.download_button(
                label=f"📥 تحميل كشف غياب وحضور ({selected_grade}) بصيغة Excel",
                data=processed_data,
                file_name=f"كشف_حضور_{selected_grade}.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            st.write(f"📋 **جدول طلاب مرحلة ({selected_grade}) الحالي:**")
            st.dataframe(df_filtered[["كود الطالب", "اسم الطالب", "المرحلة الدراسية", "حالة الحضور", "رقم تليفون الطالب"]], use_container_width=True)

with tab4:
    st.subheader("⚙️ تعديل بيانات طالب أو حذفه نهائياً")
    if not st.session_state.students_database:
        st.info("💡 قاعدة البيانات فارغة، لا يوجد طلاب لتعديلهم أو حذفهم.")
    else:
        manage_code = st.text_input("أدخل كود الطالب المراد (تعديله / حذفه):")
        
        if manage_code:
            if manage_code in st.session_state.students_database:
                current_student = st.session_state.students_database[manage_code]
                st.warning(f"⚠️ الكود يخص الطالب الحالي: **{current_student['اسم الطالب']}** ({current_student['المرحلة الدراسية']})")
                
                st.markdown("### 1️⃣ خيار التعديل (أو تبديل طالب بآخر):")
                new_name = st.text_input("الاسم الجديد (أو اسم الطالب البديل):", value=current_student['اسم الطالب'])
                new_grade = st.selectbox("المرحلة الدراسية الجديدة:", grades_list, index=grades_list.index(current_student['المرحلة الدراسية']))
                new_phone = st.text_input("رقم تليفون الطالب الجديد:", value=current_student['رقم تليفون الطالب'])
                new_father_phone = st.text_input("رقم تليفون الأب الجديد:", value=current_student['رقم تليفون الأب'])
                
                if st.button("💾 حفظ التعديلات الجديدة"):
                    st.session_state.students_database[manage_code] = {
                        "كود الطالب": manage_code,
                        "اسم الطالب": new_name,
                        "المرحلة الدراسية": new_grade,
                        "رقم تليفون الطالب": new_phone,
                        "رقم تليفون الأب": new_father_phone,
                        "حالة الحضور": current_student['حالة الحضور']
                    }
                    st.success("✅ تم تحديث بيانات الطالب بنجاح!")
                    st.rerun()
                
                st.markdown("---")
                st.markdown("### 2️⃣ خيار الحذف النهائي (إذا كان الطالب لن يحضر مجدداً):")
                if st.button("❌ حذف الطالب نهائياً من النظام", type="primary"):
                    del st.session_state.students_database[manage_code]
                    st.success("🗑️ تم حذف الطالب وإزالة كوده من الكشوفات تماماً!")
                    st.rerun()
            else:
                st.error("❌ هذا الكود غير موجود في النظام، يرجى مراجعة الرقم.")
