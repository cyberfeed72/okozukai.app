import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib      # ← 日本語対応
from datetime import datetime
from packaging import version
import os
goal = st.number_input("目標金額（円）", 0, 100000, 5000)
total = log_df["reward"].sum()
st.progress(min(total/goal, 1.0))

st.set_page_config(
    page_title="おこづかい管理アプリ",
    page_icon="💸",
    layout="centered"
)

# ---------------- ここから共通部分（初期化・讀込） ----------------
TASK_FILE = "task_list.csv"
LOG_FILE  = "task_log.csv"

def init_csvs():
    if not os.path.isfile(TASK_FILE):
        pd.DataFrame({
            "task": ["トイレ掃除", "風呂掃除", "洗い物", "料理の手伝い"],
            "reward": [50, 50, 30, 30]
        }).to_csv(TASK_FILE, index=False, encoding="utf-8-sig")

    if not os.path.isfile(LOG_FILE):
        pd.DataFrame(columns=["date", "task", "reward"]).to_csv(
            LOG_FILE, index=False, encoding="utf-8-sig"
        )

init_csvs()
tasks_df = pd.read_csv(TASK_FILE)
log_df   = pd.read_csv(LOG_FILE)

# ------------------- かわいいヘッダー -------------------
st.markdown(
    """
    <h1 style="text-align:center; font-size:2.6rem; color:#ff6f91;">
        💖 おこづかい管理アプリ
    </h1>
    """,
    unsafe_allow_html=True
)

# ------------------- お手伝いリスト編集 -------------------
st.subheader("📝 お手伝いリスト（編集できます）")
editor = st.data_editor if version.parse(st.__version__) >= version.parse("1.25.0") \
         else st.experimental_data_editor
edited_tasks = editor(tasks_df, num_rows="dynamic")
if st.button("💾 リストを保存"):
    edited_tasks.to_csv(TASK_FILE, index=False, encoding="utf-8-sig")
    st.success("保存しました！")
    st.experimental_rerun()

st.divider()

# ------------------- 報酬記録 -------------------
st.subheader("💰 報酬を記録する")
task_selected = st.selectbox("お手伝いを選択してください", edited_tasks["task"])
if st.button("📌 記録する"):
    reward_val = int(edited_tasks.loc[edited_tasks["task"] == task_selected, "reward"].values[0])
    new_entry  = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task_selected,
        "reward": reward_val
    }
    log_df = pd.concat([pd.DataFrame([new_entry]), log_df], ignore_index=True)
    log_df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
    st.success("記録しました！")
    st.experimental_rerun()

st.divider()

# ------------------- 使う・貯める・増やす -------------------
st.subheader("🏦 使う・貯める・増やす の割合")
use_p, save_p, invest_p = st.columns(3)
with use_p:
    use_perc   = st.slider("使う %", 0, 100, 20, key="use")
with save_p:
    save_perc  = st.slider("貯める %", 0, 100, 70, key="save")
with invest_p:
    invest_perc = st.slider("増やす %", 0, 100, 10, key="invest")

if use_perc + save_perc + invest_perc != 100:
    st.warning("合計が100%になるよう調整してください。")

# 円グラフ
fig, ax = plt.subplots()
labels = ["使う", "貯める", "増やす"]

if log_df.empty or log_df["reward"].sum() == 0:
    values = [1, 1, 1]   # 仮値
else:
    total = log_df["reward"].sum()
    values = [
        total * use_perc / 100,
        total * save_perc / 100,
        total * invest_perc / 100
    ]
ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis("equal")
st.pyplot(fig)

st.divider()

# ------------------- 📊 月次レポート -------------------
st.subheader("📊 月次レポート")
if log_df.empty:
    st.info("まだ履歴がありません。")
else:
    mdf = log_df.copy()
    mdf["month"] = pd.to_datetime(mdf["date"]).dt.to_period('M')
    monthly = mdf.groupby("month")["reward"].sum().reset_index()
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

    # 表示：棒グラフ
    st.bar_chart(
        data=monthly,
        x="month",
        y="reward",
        height=300
    )
    # テーブルも欲しければ
    with st.expander("テーブルで確認"):
        st.dataframe(monthly)

st.divider()
st.subheader("📜 履歴（新しい順）")
st.dataframe(log_df)
st.markdown(
    "<style>" + open("assets/style.css").read() + "</style>",
    unsafe_allow_html=True
)
