import streamlit as st
import requests
import re
import time
 
session = requests.Session() # 設定 Session

#st.session_state.user_id
#st.session_state.accessToken
user_id = ""
accessToken = ""
courses_name_list = []
courses_id_list = []

def login(email, password):
    
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
        user_id = re.search("\d{7}", re.search("var user_id = \d{7}", response.text).group()).group()
        accessToken = re.search("\w{40}", re.search('var accessToken = "\w{40}";', response.text).group()).group()
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
    for i in range(len(response.json()['courses'])):
        if(response.json()['courses'][i]['teacher_name'] != "Zuvio \u5b98\u65b9\u6d3b\u52d5"):
            courses_name_list.append(response.json()['courses'][i]['course_name'])
            courses_id_list.append(response.json()['courses'][i]['course_id'])
        #print(a['courses'][i]['course_id'])
    print(courses_name_list)
    print(courses_id_list)



def rollcall(lesson_id, lat, lng):
    getrollid = session.get("https://irs.zuvio.com.tw/student5/irs/rollcall/"+str(lesson_id))
    #makerollcall_id = re.search("makeRollcall\(\d\d\d\d\d\d\d\)", getrollid.text).group()
    #user_id = re.search("\d{7}", re.search("var user_id = \d{7}", getrollid.text).group()).group()
    #accessToken = re.search("\w{40}", re.search('var accessToken = "\w{40}";', getrollid.text).group()).group()
    print(user_id)
    print(accessToken)
    try:
        rollcall_id = re.search("\d{7}", re.search("makeRollcall\(\d{7}\)", getrollid.text).group()).group()
        print(rollcall_id)

        rollcall_url = "https://irs.zuvio.com.tw/app_v2/makeRollcall"
        data = {
            'user_id': user_id,
            'accessToken': accessToken,
            'rollcall_id': rollcall_id,
            'device': "WEB",
            'lat': lat,
            'lng': lng
        }

        rollcall = session.post(rollcall_url, data=data)
        print("rollcall status:"+str(rollcall.status_code))
        return True
    except:
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
    progress_text = "正在取得課程清單"
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()

def main():


    st.write("### 🕊️Zuvio簽到系統")
    if 'user_id' not in st.session_state:
        login_ui()
    else:
        logout()
        rollcall_section()
        




main()
            




