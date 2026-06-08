"""
!!!!!!!!!!!!⭐꼭 읽고 프로그램을 사용하시오⭐!!!!!!!!!!!!!!!
해당 프로그램은 <📚과목별 랜덤 문제 뽑기 프로그램>입니다.

실행 방법:
1. 프로그램을 처음 실행하면 과목 목록을 입력합니다.
   예: 진동공학, 수치해석, 시스템제어
2. 입력한 과목에 맞게 study_questions 폴더가 자동으로 생깁니다.
3. 각 과목의 problems 폴더에는 문제 사진을 넣어주세요.
4. 각 과목의 answers 폴더에는 같은 이름의 해설 사진을 넣어주세요.

예시:
study_questions/진동공학/problems/q001.png
study_questions/진동공학/answers/q001.png

주의:
- 사진은 png 또는 gif 파일만 넣어주세요. (jpeg 파일은 tk.PhotoImage가 표시하지 못할 수 있습니다.)
- 프로그램을 실행한 적이 있어 이미 폴더가 있으면, 폴더를 새로 만들지 않고 그대로 사용하니 걱정하지 마세요~~~~
"""

import os
import json
import random
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import date


# 폴더와 파일 이름을 변수로 저장한다.
question_folder = "study_questions" #폴더 구조의 제일 상단에 위치하는, 상위 폴더의 이름은 study_questions
record_file = "today_record.json"
subject_file = "subjects.json"

# 과목 이름을 저장할 리스트이다.
subjects = []

# 현재 선택한 과목과 현재 문제 정보를 저장할 변수이다.
selected_subject = ""
current_question = None
current_image = None

# 오늘의 기록을 저장할 딕셔너리이다.
record = {}


# 과목 목록을 json 파일에 저장한다.
def save_subjects(subject_list):
    with open(subject_file, "w", encoding="utf-8") as f:
        json.dump(subject_list, f, ensure_ascii=False, indent=2)


# 과목 목록을 불러온다. 처음 실행이면 사용자에게 과목을 입력받는다.
def load_subjects():
    if os.path.exists(subject_file):
        with open(subject_file, "r", encoding="utf-8") as f:
            saved_subjects = json.load(f)

        if len(saved_subjects) > 0:
            return saved_subjects

    # 처음 실행할 때만 작은 입력창을 띄운다.
    setup_window = tk.Tk()
    setup_window.withdraw()

    text = simpledialog.askstring(
        "과목 설정",
        "처음 사용할 과목명을 쉼표로 구분해서 입력하세요.\n\n예: 진동공학, 수치해석, 시스템제어"
    )

    setup_window.destroy()

    if text is None or text.strip() == "":
        messagebox.showinfo("안내", "입력한 과목이 없어서 '기본과목' 폴더를 만듭니다.")
        subject_list = ["기본과목"]
    else:
        subject_list = []
        for subject in text.split(","):
            subject = subject.strip()
            if subject != "":
                subject_list.append(subject)

    save_subjects(subject_list)
    return subject_list


# 과목별 문제 폴더와 해설 폴더를 만든다.
def make_folders():
    for subject in subjects: #폴더 구조의 하위 폴더의 이름은 각각 problems랑 answers! readme나 설계문서의 폴더 구조 그림 참고하기! 
        os.makedirs(os.path.join(question_folder, subject, "problems"), exist_ok=True)
        os.makedirs(os.path.join(question_folder, subject, "answers"), exist_ok=True)


# 오늘 날짜에 맞는 새 기록을 만든다.
def make_new_record():
    return {
        "date": str(date.today()),
        "solved": 0,
        "correct": 0
    }


# 저장된 기록을 불러온다.
def load_record():
    if not os.path.exists(record_file):
        new_record = make_new_record()
        save_record(new_record)
        return new_record

    with open(record_file, "r", encoding="utf-8") as f:
        saved_record = json.load(f)

    # 날짜가 바뀌었으면 오늘 기록을 0으로 초기화한다.
    if saved_record["date"] != str(date.today()):
        saved_record = make_new_record()
        save_record(saved_record)

    return saved_record


# 기록을 json 파일에 저장한다.
def save_record(record_data):
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(record_data, f, ensure_ascii=False, indent=2)


# 정답률을 계산한다.
def get_accuracy():
    if record["solved"] == 0:
        return 0
    return record["correct"] / record["solved"] * 100


# 화면 위쪽의 오늘 기록 문장을 바꾼다.
def update_record_label():
    accuracy = get_accuracy()
    record_label.config(
        text=f"오늘 푼 문제: {record['solved']}개 / 오늘 맞힌 문제: {record['correct']}개 / 정답률: {accuracy:.1f}%"
    )


# 특정 폴더 안에서 이미지 파일만 찾아 리스트로 만든다.
def get_image_files(folder_path):
    image_files = []

    if not os.path.exists(folder_path):
        return image_files

    for file_name in os.listdir(folder_path):
        lower_name = file_name.lower()
        if lower_name.endswith(".png") or lower_name.endswith(".gif"):
            image_files.append(file_name)

    return image_files


# 선택한 과목에서 랜덤 문제 하나를 뽑는다.
def get_random_question():
    question_list = []

    # 전체 과목 랜덤을 선택하면 모든 과목에서 문제를 찾는다.
    if selected_subject == "전체 과목 랜덤":
        search_subjects = subjects
    else:
        search_subjects = [selected_subject]

    for subject in search_subjects:
        problem_path = os.path.join(question_folder, subject, "problems")
        answer_path = os.path.join(question_folder, subject, "answers")
        image_files = get_image_files(problem_path)

        for file_name in image_files:
            question = {
                "subject": subject,
                "problem": os.path.join(problem_path, file_name),
                "answer": os.path.join(answer_path, file_name),
                "file_name": file_name
            }
            question_list.append(question)

    if len(question_list) == 0:
        return None

    return random.choice(question_list)


# 이미지를 화면에 보여준다.
def show_image(image_path):
    global current_image

    current_image = tk.PhotoImage(file=image_path)
    image_label.config(image=current_image, text="")


# 과목 버튼을 눌렀을 때 실행된다.
def select_subject(subject):
    global selected_subject
    selected_subject = subject
    load_new_problem()


# 새 문제를 불러온다.
def load_new_problem():
    global current_question

    if selected_subject == "":
        info_label.config(text="먼저 과목을 선택하세요.")
        return

    current_question = get_random_question()

    if current_question is None:
        info_label.config(text="문제 이미지가 없습니다. problems 폴더에 png 또는 gif 파일을 넣어주세요.")
        image_label.config(image="", text="문제 이미지 없음")
        finish_button.config(state="disabled")
        correct_button.config(state="disabled")
        wrong_button.config(state="disabled")
        return

    info_label.config(text=current_question["subject"] + " 랜덤 문제: " + current_question["file_name"])
    show_image(current_question["problem"])

    finish_button.config(state="normal")
    correct_button.config(state="disabled")
    wrong_button.config(state="disabled")


# 다 풀었다 버튼을 누르면 해설을 보여준다.
def show_answer():
    if current_question is None:
        return

    answer_path = current_question["answer"]

    if not os.path.exists(answer_path):
        info_label.config(text="해설 이미지가 없습니다. answers 폴더에 같은 이름의 파일을 넣어주세요: " + current_question["file_name"])
        return

    info_label.config(text="해설 확인: 맞혔는지 틀렸는지 선택하세요.")
    show_image(answer_path)

    finish_button.config(state="disabled")
    correct_button.config(state="normal")
    wrong_button.config(state="normal")


# 맞혔다 또는 틀렸다 버튼을 눌렀을 때 기록을 수정한다.
def update_result(is_correct):
    record["solved"] = record["solved"] + 1

    if is_correct == True:
        record["correct"] = record["correct"] + 1

    save_record(record)
    update_record_label()

    info_label.config(text="기록 저장 완료! 다음 문제를 풀어보세요.")
    correct_button.config(state="disabled")
    wrong_button.config(state="disabled")
    finish_button.config(state="disabled")


# -------------------- 프로그램 시작 부분 --------------------
subjects = load_subjects()
make_folders()
record = load_record()

window = tk.Tk()
window.title("과목별 랜덤 문제 뽑기")
window.geometry("850x650")

# 제목을 보여준다.
title_label = tk.Label(window, text="과목별 랜덤 문제 뽑기", font=("맑은 고딕", 18, "bold"))
title_label.pack(pady=10)

# 오늘 기록을 보여준다.
record_label = tk.Label(window, text="", font=("맑은 고딕", 12))
record_label.pack(pady=5)

# 안내 문구를 보여준다.
info_label = tk.Label(window, text="복습할 과목을 선택하세요.", font=("맑은 고딕", 12))
info_label.pack(pady=5)

# 과목 버튼들을 담을 프레임이다.
subject_frame = tk.Frame(window)
subject_frame.pack(pady=5)

# 과목 버튼을 반복문으로 만든다.
for subject in subjects:
    button = tk.Button(subject_frame, text=subject, width=18, command=lambda s=subject: select_subject(s))
    button.pack(side="left", padx=3, pady=3)

all_button = tk.Button(window, text="전체 과목 랜덤", width=20, command=lambda: select_subject("전체 과목 랜덤"))
all_button.pack(pady=5)

# 이미지를 보여줄 영역이다.
image_label = tk.Label(window, text="여기에 문제 이미지가 표시됩니다.", width=90, height=25, bg="white", relief="solid")
image_label.pack(padx=10, pady=10)

# 기능 버튼들을 담을 프레임이다.
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

finish_button = tk.Button(button_frame, text="다 풀었다", width=15, command=show_answer, state="disabled")
finish_button.pack(side="left", padx=5)

correct_button = tk.Button(button_frame, text="맞혔다", width=15, command=lambda: update_result(True), state="disabled")
correct_button.pack(side="left", padx=5)

wrong_button = tk.Button(button_frame, text="틀렸다", width=15, command=lambda: update_result(False), state="disabled")
wrong_button.pack(side="left", padx=5)

next_button = tk.Button(button_frame, text="다음 문제", width=15, command=load_new_problem)
next_button.pack(side="left", padx=5)

update_record_label()
window.mainloop()
