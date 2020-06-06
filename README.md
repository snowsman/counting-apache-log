Counting Apache Log
===================
Count Apache log file by time/remote host and display it in a table.  
Apacheログファイルを時間/リモートホスト別に集計し, 件数をテーブルで表示します.


# Requirements
* Python 3.x
* Numpy


# Supported log format
```%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\```

# Usage
1. Run "main.py".  
   main.pyを起動する.
2. Select apache log files.  
   Apacheログファイル（複数選択可能）を選択する.
3. Answer "Please input a number that is greater than or equal to the number of remote host.(Default: 100000)" to type integer or press enter.You'll need to take into account the size of the log files and the amount of memory.  
   ログファイルに出現する重複なしでのリモートホストの数以上の値を入力するか, デフォルトの値でよければEnterキーを押す. ファイルの容量とメモリの容量を考慮して決めるとよい.
4. Answer "Do you want to specify the period of time to be counted?" to Yes (or, y, yes) or No (or, n, N, no).  
   集計する期間を指定するかどうか, Yes (or, y, yes) か No (or, n, N, no) で答える.
5. (If you answer Yes, answer "Please input the start date. eg: 2020/06/01" to %Y%m%d.)  
   (上の質問でYesと答えた場合は, 集計の開始期間を %Y/%m/%d 形式で答える.)
6. (If you answer Yes, answer "Please input the start date. eg: 2020/06/01" to %Y%m%d.)  
   (上の質問で答えた場合は, 集計の終了期間を %Y/%m/%d 形式で答える.)
7. Answer "How many remote hosts do you want to show? (Default: 20)	" to type integer or press enter.  
   リモートホストを上位何件表示したいか入力するか, デフォルトの値でよければEnterキーを押す.
8. The table of results will be showed.  
   結果のテーブルが表示される.
