
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib 
import matplotlib
matplotlib.rcParams['font.family'] = 'IPAexGothic'   # or 'Noto Sans JP'
from datetime import datetime
from packaging import version
import os

st.set_page_config(page_title="おこづかい管理アプリ", page_icon="💴", layout="centered")

# === ファイルパス ===
TASK_FILE = "task_list.csv"
LOG_FILE = "task_log.csv"

# === 初期化 ===
def init_csvs():
    if not os.path.isfile(TASK_FILE) or os.path.getsize(TASK_FILE) == 0:
        df_init = pd.DataFrame({
            "task": ["トイレ掃除", "風呂掃除", "洗い物", "料理の手伝い"],
            "reward": [50, 50, 30, 30]
        })
        df_init.to_csv(TASK_FILE, index=False, encoding="utf-8-sig")
    if not os.path.isfile(LOG_FILE):
        pd.DataFrame(columns=["date", "task", "reward"]).to_csv(LOG_FILE, index=False, encoding="utf-8-sig")

init_csvs()

# === データ読み込み ===
tasks_df = pd.read_csv(TASK_FILE)
log_df = pd.read_csv(LOG_FILE)

st.title("おこづかい管理アプリ")

# --- 関数：互換性のための data_editor ラッパー ---
def compatible_data_editor(df):
    """Streamlit バージョンに応じて data_editor / experimental_data_editor を呼び出す"""
    if version.parse(st.__version__) >= version.parse("1.25.0"):
        editor_fn = st.data_editor
    else:
        editor_fn = st.experimental_data_editor

    try:
        return editor_fn(df, num_rows="dynamic")
    except TypeError:
        # 古いバージョンで num_rows がサポートされていない場合
        return editor_fn(df)

# --- お手伝いリスト編集 ---
st.header("📝 お手伝いリスト（編集できます）")
edited_tasks = compatible_data_editor(tasks_df)
if st.button("リストを保存"):
    edited_tasks.to_csv(TASK_FILE, index=False, encoding="utf-8-sig")
    st.success("保存しました！")
    st.experimental_rerun()

st.divider()

# --- 報酬記録 ---
st.header("💰 報酬を記録する")
task_selected = st.selectbox("お手伝いを選択してください", edited_tasks["task"])
if st.button("記録する"):
    reward_val = int(edited_tasks.loc[edited_tasks["task"] == task_selected, "reward"].values[0])
    new_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task_selected,
        "reward": reward_val
    }
    log_df = pd.concat([pd.DataFrame([new_entry]), log_df], ignore_index=True)
    log_df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
    st.success("記録しました！")
    st.experimental_rerun()

st.divider()

# --- 使う・貯める・増やす 設定 ---
st.header("🏦 使う・貯める・増やす の割合")
col1, col2, col3 = st.columns(3)
with col1:
    use_perc = st.slider("使う %", 0, 100, 20, key="use")
with col2:
    save_perc = st.slider("貯める %", 0, 100, 70, key="save")
with col3:
    invest_perc = st.slider("増やす %", 0, 100, 10, key="invest")

total_perc = use_perc + save_perc + invest_perc
if total_perc != 100:
    st.warning(f"割合の合計が {total_perc}% です。100% になるよう調整してください。")

# --- 円グラフ ---
st.header("📈 3分法グラフ")
fig, ax = plt.subplots()
labels = ["使う", "貯める", "増やす"]

if len(log_df) == 0:
    ax.pie([1, 1, 1], labels=labels, autopct='%1.1f%%', startangle=90)
else:
    total_reward = log_df["reward"].sum()
    if total_reward == 0:
        values = [1, 1, 1]
    else:
        values = [
            total_reward * use_perc / 100,
            total_reward * save_perc / 100,
            total_reward * invest_perc / 100
        ]
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)

ax.axis("equal")
st.pyplot(fig)

st.divider()
st.header("📜 履歴（新しい順）")
st.dataframe(log_df)
