# Platform Engagement Dashboard for 365 Data Science

When seeking entry-level data science jobs, having a strong portfolio is essential, and a project can be the essence of that portfolio. By working on a real-life project from the beginning, you can showcase various data-related skills to potential employers. One excellent project brief to consider is The 365 Learning Data Challenge, which allows you to test your creative and analytical thinking by exploring user engagement in e-Learning platforms. Moreover, the required data is already available, making it easier to get started.

This blog post will present my final project deliverable and walk you through the various steps involved in its creation, such as querying data, visualization, and incorporating elements of storytelling.

<h3>Final Deliverable</h3>

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
Tableau Dashboard tracking User Engagement of 365 Data Science from 1 Jan to 20 Oct – <a href="https://public.tableau.com/app/profile/marcus.le1600/viz/365DS_16761251940980/PlatformEngagementDashboard" target="_blank">Link</a>
</div>

<h3>1. Upload data to BigQuery</h3>

After downloading the data files, you can manipulate data locally using Python or Excel. I, however, recommend using a cloud-based storage service (I use BigQuery Free Plan), then using local SQL statements to retrieve the wanted data that would be used in the dashboard.

In BigQuery, we’ll start by creating a dataset, then uploading each CSV file in the dataset. Remember to take a look at the schema for each table, partition and cluster them accordingly.

<h3>Final Deliverable</h3>

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">The dataset for the project</div>

We can try writing some DML SQL statements in the Query Editor to get the feel of the dataset, since we will mostly use SQL in the next step.

<h3>2. Query & Manipulate data using Pandas & SQL</h3>

In order to retrieve the data locally, we have to enable BigQuery API, install BigQuery Client Library, and make an API call to run a query using the following Python codes:


```python
from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './service-account.json'
client = bigquery.Client()

student_watch_time = """
SELECT S.student_id,
 L.minutes_watched,
 L.date_watched
FROM `database-376007.365_database.365_student_info` S
JOIN `database-376007.365_database.365_student_learning` L
ON S.student_id = L.student_id
"""

swt_df = client.query(student_watch_time).to_dataframe()
```

Avoid delving too deeply into specific insights at this stage. Instead, focus on constructing queries that have the potential to have interesting and informative results. Take a closer look at the significance of the outcomes and investigate any related tables that might cause or result from them.

To assist you in this process, below are some of the queries that I use as the final CSV files to connect to Tableau. Note that you can use more simple queries and then use Pandas to manipulate data.

```python
monthly_active_users_count = """
SELECT COUNT(DISTINCT student_id), EXTRACT (MONTH FROM date_engaged) M
FROM `database-376007.365_database.365_student_engagement` 
GROUP BY M
ORDER BY M
"""

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
```

<h3>3. Store CSV files & connect to Tableau</h3>

Remember to transform each query into the dataframe and export them into CSV files:


```python
swt_df = client.query(student_watch_time).to_dataframe()
swt_csv = swt_df.to_csv('student_watch_time.csv', index=False)
```

It is now time to connect the files to Tableau. There are two options: you can either connect the local files directly to Tableau, or push the files to Google Drive via the Google Drive API and then connect them to Tableau. The following example code is for the latter option:


```python
upload_files = ['top_5_rated_courses.csv', 'top_5_watched_courses.csv', 'students_master.csv',
'student_watch_time.csv', 'daily_active_users.csv']

for file in upload_files:
  headers = {
    "Authorization":"Bearer ###your-access-token###"
  }
  para = {
      "name":file,
      "parents":["###permalink-to-directory-folder###"]
  }
  files = {
      'data':('metadata',json.dumps(para),'application/json;charset=UTF-8'),
      'file':open(f'./{file}','rb')
  }
  r = requests.post("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
      headers=headers,
      files=files
  )
```

If you have successfully connected your CSV files to Tableau, you will be able to view it in Data Source tab:

# Image for the tab

<h3>4. Visualization & Analysis</h3>

During the visualization process in Tableau, it’s useful to consider a hypothetical business scenario to determine which visualizations are relevant. In my case, I chose to focus on several key metrics related to high-rating and popular courses, users’ funnels and purchase trends, and active – new users over time.

When selecting visualizations, try to keep in mind the principle of less is more. While it’s tempting to include every charts possible to showcase all findings, it’s important to choose the right visualizations without cluttering the dashboard. A clean and concise dashboard will not only be more visually appealing, but it will also be easier for the audience to interpret.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">Dashboard (without textual insights)</div>

The final step is to add insightful text to support each graph. This text should provide context and help viewers understand the key takeaways from the data, making the dashboard more comprehensive and impactful. By taking the time to thoughtfully craft this text, we can effectively communicate insights and even recommend actions based on the data.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">Our final dashboard</div>

<h3>Other resources</h3>

Tutorial for BigQuery API: <a href="https://www.youtube.com/watch?v=lLPdRRy7dfE" target="_blank">YouTube</a>

Tutorial for Google Drive API: <a href="https://www.youtube.com/watch?v=JwGzHitUVcU" target="_blank">YouTube</a>
