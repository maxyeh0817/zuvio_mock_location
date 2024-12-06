import streamlit as st
import requests
import re
import time
 
session = requests.Session() # 設定 Session

user_id = ""
accessToken = ""
courses_name_list = []
courses_id_list = []

def login(email, password):
    
    st.session_state.email = email
    st.session_state.password= password

    login = "https://irs.zuvio.com.tw/irs/submitLogin"
    data = {
        'email': email,
        'password': password,
        'current_language': "zh-TW"
    }

    response = session.post(login, data=data)
    print("login status:"+str(response.status_code))

def getidentity():
    try:
        article = "https://irs.zuvio.com.tw/student5/chickenM/articles"
        response = session.get(article)
        global user_id
        global accessToken
        user_id = re.search(r"\d{7}", re.search(r"var user_id = \d{7}", response.text).group()).group()
        accessToken = re.search(r"\w{40}", re.search(r'var accessToken = "\w{40}";', response.text).group()).group()
        st.session_state.user_id = user_id
        st.session_state.accessToken = accessToken
        return True
    except:
        return False
 
def courses(user_id, accessToken):
    url = f"https://irs.zuvio.com.tw/course/listStudentCurrentCourses?user_id={user_id}&accessToken={accessToken}"
    response = session.get(url)

    global courses_name_list
    global courses_id_list
    courses_name_list = []
    courses_id_list = []
    for i in range(len(response.json()['courses'])):
        if(response.json()['courses'][i]['teacher_name'] != "Zuvio \u5b98\u65b9\u6d3b\u52d5"):
            courses_name_list.append(response.json()['courses'][i]['course_name'])
            courses_id_list.append(response.json()['courses'][i]['course_id'])
            st.session_state.courses_name_list = courses_name_list
            st.session_state.courses_id_list = courses_id_list
    print(courses_name_list)
    print(courses_id_list)
    print(st.session_state.courses_name_list)
    print(st.session_state.courses_id_list)
    



def rollcall(lesson_id, lat, lng):


    login(st.session_state.email,st.session_state.password)
    getidentity()

    url = f"https://irs.zuvio.com.tw/student5/irs/rollcall/{lesson_id}"
    getrollid = session.get(url)
    print(getrollid.status_code)
    try:
        f = open("test.html", "w")
        f.write(getrollid.text)
        f.close()
        rollcall_id = re.search(r"\d{7}", re.search(r"makeRollcall\(\d{7}\)", getrollid.text).group()).group()
        print(rollcall_id)

        rollcall_url = "https://irs.zuvio.com.tw/app_v2/makeRollcall"
        data = {
            'user_id': st.session_state.user_id,
            'accessToken': st.session_state.accessToken,
            'rollcall_id': rollcall_id,
            'device': "WEB",
            'lat': lat,
            'lng': lng
        }

        rollcall = session.post(rollcall_url, data=data)
        print("rollcall status:"+str(rollcall.status_code))
        return True
    except Exception as e:
        print(e)
        print("not in rollcall time")
        return False
    


#ui
def login_ui():
    with st.form("Login"):
        account = st.text_input("email:")
        password = st.text_input("password:", type="password")
        if st.form_submit_button("登入"):
            login(account, password)
            if getidentity():
                st.toast('登入成功! 正在跳轉......', icon='🎉')
                print(st.session_state.user_id)
                print(st.session_state.accessToken)
                time.sleep(3)
                st.rerun()
            else:
                st.toast('登入失敗!', icon='😞')
                try:
                    del st.session_state.user_id
                    del st.session_state.accessToken
                    st.rerun()
                except:
                    print("無需登出")

def logout():
    if st.button("登出"):
        st.toast('登出成功! 正在跳轉......', icon='🎉')
        del st.session_state.user_id
        del st.session_state.accessToken
        del st.session_state.email
        del st.session_state.password
        try:
            del st.session_state.courses_name_list
            del st.session_state.courses_id_list
        except:
            print("no need to refresh....")
        time.sleep(3)
        st.rerun()
    if st.button("刷新課程清單"):
        try:
            del st.session_state.courses_name_list
            del st.session_state.courses_id_list
            st.rerun()
        except:
            print("no need to refresh....")
    st.write("___")

def rollcall_section():
    if 'courses_name_list' not in st.session_state:
        progress_text = "正在取得課程清單"
        my_bar = st.progress(0, text=progress_text)

        courses(st.session_state.user_id, st.session_state.accessToken)

        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(1)
        my_bar.empty()
        time.sleep(1)
        st.rerun()
    else:
        option = st.selectbox("選擇要簽到的課程", st.session_state.courses_name_list)
        place = st.selectbox("選擇地點", ["北科三教", "北科二教", "自訂"])
        if place == "自訂":
            col1, col2= st.columns(2)

            with col1:
                custom_lat = st.text_input("請輸入經度")

            with col2:
                custom_lng = st.text_input("請輸入緯度")
        if st.button("簽到"):
            lesson_id_list = st.session_state.courses_name_list
            print(st.session_state.courses_id_list[lesson_id_list.index(option)])
            if place == "北科三教":
                lat = "25.042909922425178"
                lng = "121.53470727260711"
            elif place == "北科二教":
                lat = "25.043467295972942"
                lng = "121.53444746920269"
            elif place == "自訂":
                lat = custom_lat
                lng = custom_lng
            if rollcall(st.session_state.courses_id_list[lesson_id_list.index(option)], lat, lng):
                st.toast('簽到成功!', icon='🎉')
            else:
                st.toast('簽到失敗!課程目前無開放簽到', icon='😞')

def main():
    st.write("### 🕊️Zuvio簽到系統")
    if 'user_id' not in st.session_state:
        login_ui()
    else:
        logout()
        rollcall_section()
        
if __name__ == '__main__':
    main()
            




