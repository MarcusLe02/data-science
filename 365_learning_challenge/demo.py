from google.cloud import bigquery
import pandas as pd
import os
import json
import requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/Users/marcusle02/Downloads/service-account.json'
client = bigquery.Client()

top_5_rated_courses = """
SELECT CI.course_title, AVG(CR.course_rating) AS avg_rating, COUNT(DISTINCT CR.student_id) AS num_ratings,  SUM(SL.minutes_watched)/COUNT(DISTINCT CR.student_id) AS total_watched_time, COUNT(DISTINCT SL.student_id) AS num_watches
FROM `database-376007.365_database.365_course_info` CI
LEFT JOIN `database-376007.365_database.365_course_ratings` CR ON CI.course_id = CR.course_id
LEFT JOIN (
  SELECT course_id, student_id, SUM(minutes_watched) AS minutes_watched
  FROM `database-376007.365_database.365_student_learning`
  GROUP BY course_id, student_id
) SL ON CI.course_id = SL.course_id
GROUP BY CI.course_id, CI.course_title
ORDER BY AVG(CR.course_rating) DESC
LIMIT 5;
"""

top_5_watched_courses = """
SELECT CI.course_title, AVG(CR.course_rating) AS avg_rating, COUNT(DISTINCT CR.student_id) AS num_ratings,  SUM(SL.minutes_watched)/COUNT(DISTINCT CR.student_id) AS total_watched_time, COUNT(DISTINCT SL.student_id) AS num_watches
FROM `database-376007.365_database.365_course_info` CI
LEFT JOIN `database-376007.365_database.365_course_ratings` CR ON CI.course_id = CR.course_id
LEFT JOIN (
  SELECT course_id, student_id, SUM(minutes_watched) AS minutes_watched
  FROM `database-376007.365_database.365_student_learning`
  GROUP BY course_id, student_id
) SL ON CI.course_id = SL.course_id
GROUP BY CI.course_id, CI.course_title
ORDER BY SUM(SL.minutes_watched) DESC
LIMIT 5;
"""

students_master = """
SELECT 
  S.student_id,
  S.student_country,
  S.date_registered, 
  CASE WHEN EXISTS (SELECT 1 FROM `database-376007.365_database.365_student_purchases` WHERE student_id = S.student_id) THEN 'YES' ELSE 'NO' END AS has_purchased,
  CASE WHEN EXISTS (SELECT 1 FROM `database-376007.365_database.365_student_engagement` WHERE student_id = S.student_id) THEN 'YES' ELSE 'NO' END AS has_onboarded,
FROM 
  `database-376007.365_database.365_student_info` S
"""

student_watch_time = """
SELECT S.student_id,
  L.minutes_watched,
  L.date_watched
FROM `database-376007.365_database.365_student_info` S
JOIN `database-376007.365_database.365_student_learning` L
ON S.student_id = L.student_id
"""

daily_active_users = """
SELECT 
    COUNT(DISTINCT student_id), date_engaged
FROM 
 `database-376007.365_database.365_student_engagement` 
GROUP BY date_engaged
ORDER BY date_engaged
"""

monthly_active_users = """
SELECT 
    COUNT(DISTINCT student_id), EXTRACT (MONTH FROM date_engaged) M
FROM 
 `database-376007.365_database.365_student_engagement` 
GROUP BY M
ORDER BY M
"""

student_active_days = """
SELECT 
    student_id, COUNT(DISTINCT date_engaged)
FROM 
 `database-376007.365_database.365_student_engagement` 
GROUP BY student_id
"""

t5rc_df = client.query(top_5_rated_courses).to_dataframe()
t5wc_df = client.query(top_5_watched_courses).to_dataframe()
sm_df = client.query(students_master).to_dataframe()
swt_df = client.query(student_watch_time).to_dataframe()
dau_df = client.query(daily_active_users).to_dataframe()
mau_df = client.query(monthly_active_users).to_dataframe()
sad_df = client.query(student_active_days).to_dataframe()


t5rc_csv = t5rc_df.to_csv('top_5_rated_courses.csv', index=False)
t5wc_csv = t5wc_df.to_csv('top_5_watched_courses.csv', index=False)
sm_csv = sm_df.to_csv('students_master.csv', index=False)
swt_csv = swt_df.to_csv('student_watch_time.csv', index=False)
dau_csv = dau_df.to_csv('daily_active_users.csv', index=False)
mau_csv = mau_df.to_csv('monthly_active_users.csv', index=False)
sad_csv = sad_df.to_csv('student_active_days.csv', index=False)


upload_files = ['top_5_rated_courses.csv', 'top_5_watched_courses.csv', 'students_master.csv',
'student_watch_time.csv', 'daily_active_users.csv', 'monthly_active_users.csv','student_active_days.csv']

for file in upload_files:
  headers = {
    "Authorization":"Bearer ya29.a0AVvZVsqVJG5POmVsLlU6lr-ymdLD_nnEQECszTvM0GKwqKKH8W66g84vuSGShrA0B_Bd3nq56KA1-wdPKu2VMbcxnIWWDrmtxTMieguAU8bNPccJh2dJJbq5i9IAV_LHOyddK4ZMlw-ltfUmhwKQ2l6j1JO1YMIaCgYKARQSAQASFQGbdwaIR_Pxcc6bKkgSaVtm9eZyEA0166"
  }
  para = {
      "name":file,
      "parents":["1PhlRUhup-90_Qte7g9IhVEpYpebnyufZ"]
  }
  files = {
      'data':('metadata',json.dumps(para),'application/json;charset=UTF-8'),
      'file':open(f'./{file}','rb')
  }
  r = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
      headers=headers,
      files=files
  )