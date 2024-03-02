# A Walkthrough into automating Excel reports with openpyxl

Oh, Excel reporting! The mere thought of it sends chills down my spine. I can hear my colleague’s voice in my head saying, “Excel reporting is a pain, a real pain!” And let’s face it, no matter how fancy tools we use, we always end up back in Excel. Why? Because everyone knows how to use it. But at what cost? Endless hours of scrolling, applying formulas, and scrolling again. It’s like being trapped in a never-ending maze of cells, with no escape in sight. Even if you find the way out, there is still a repetitive work of updating 20 Excel charts for the weekly report waiting.

With that being said, there are benefits with Excel charts. They are highly customizable and allow for easy creation of visuals and add-ons to highlight observations that support findings. They are also often seamlessly integrated into other Microsoft Office suite, making them an essential part of many slide decks and reports on a regular basis.

Taking into account the laborious yet accessible nature of manual Excel reporting, I attempted to automate the process using Python library openpyxl. We’ll walk through each step of the process, from accessing and manipulating data to generating charts. By the end of this post, you’ll have a solid understanding of how to streamline your Excel reporting workflow, as well as its pros and cons.

<h3>Problem statement</h3>

Imagine you are a Data Analyst who has received a real-time Excel file containing all sales orders from the Data Engineer team. Your job is to create the weekly Sales Report using PowerPoint and to create the necessary charts from the raw data to put in the slide deck.

The manual process of creating these charts is a daunting task that requires the following steps:

<ul>
    <li>Extract and transform raw data: Format data types, add extra columns, and apply formulas for better understanding and usability.</li>
    <li>Create pivot tables: Aggregate raw data to facilitate improved visualization and analysis.</li>
    <li>Create charts from pivot tables: Generate charts to enhance the visualization of data and extract insights.</li>
    <li>Format charts: Ensure visually appealing and clear representation of insights by formatting charts.</li>
</ul>

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid path="assets/img/9.jpg" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">Sample pivot excel table</div>

This process can be time-consuming and error-prone, especially when dealing with large datasets. Let’s see if we automate this process using Python and openpyxl library, can we save time and improve the accuracy of our reports.

I would use the sample sales data from Kaggle for the Python implementation, but you could choose any dataset you like to follow.

<h3>Implementation</h3>

Import libraries

We’ll use the following libraries:

```python
import pandas as pd
import datetime
from openpyxl import *
from openpyxl.chart import *
from openpyxl.styles import Font
```

Pandas will be used to read the Excel file, write formulas, create pivot tables, and write to a single Excel file. Openpyxl will be used to create charts and format the spreadsheet, and datetime will be used to save the report as the working date.

Read Excel file & add formulas
Use the following code to read the necessary columns from the Excel file:

```python
excel_df = pd.read_excel('sales_data_sample.xlsx')
excel_df = excel_df[['QUANTITYORDERED', 'PRICEEACH', 'ORDERDATE', 'PRODUCTLINE', 'PHONE', 'COUNTRY']]
```

# image for current excel_df

You might notice that each record only contains the unit price and its quantity, thus we need to add a column to calculate the total price of the order. Also, the data frame does not recognize the order date as a datetime data type, then we need to manipulate it a bit:

```python
excel_df['TOTALPRICE'] = excel_df['QUANTITYORDERED'] * excel_df['PRICEEACH']
excel_df['ORDERDATE'] = pd.to_datetime(excel_df['ORDERDATE'])
excel_df['MONTH_ID'] = excel_df['ORDERDATE'].dt.month
excel_df['YEAR_ID'] = excel_df['ORDERDATE'].dt.year
```

In Excel, the process of creating formula columns is more cumbersome as we need to add a new column, remember the cells to reference the formula on, and copy to the whole column. In Python, we can do it intuitively by using the field names in the calculation.

Creating pivot tables

We can create pivot tables easily with the df.pivot_tables() function. Here are some examples of pivot tables that I use:

```python
yearly_sales = excel_df.pivot_table(columns='YEAR_ID', values='TOTALPRICE', aggfunc='sum')

ytd_sales_by_country = excel_df[excel_df.YEAR_ID == excel_df.YEAR_ID.max()].pivot_table(index='COUNTRY', columns='YEAR_ID', values='TOTALPRICE', aggfunc='sum')

ytd_monthly_orders = excel_df[excel_df.YEAR_ID == excel_df.YEAR_ID.max()].pivot_table(index='MONTH_ID', values='PHONE', aggfunc='count')
```

There are a few differences when using pivot tables in Python and Excel: the index parameter is used instead of rows in Excel, and the filter must be applied before using the pivot table. This makes the filter harder to use than in Excel, but it allows filtering with more complex conditions.

Exporting pivot tables to Excel file
After creating the pivot tables, we can save them as sheets in an Excel file with the ExcelWriter function:

```python
today = datetime.datetime.today().strftime('%d%m%y')

with pd.ExcelWriter(f"Report_{today}.xlsx") as writer:
    yearly_sales.to_excel(writer, sheet_name="Yearly Sales")
    ytd_sales_by_country.to_excel(writer, sheet_name="Yearly Sales")
    ytd_monthly_orders.to_excel(writer, sheet_name="YTD Monthly Orders")
```
Now the Excel file is exported in the same folder your Python script is located, and it is named with the creation date like Report_180322, which means the file is created on 18 March, 2022.

Manipulate Excel file with openpyxl
We will use the openpyxl library to create charts from the pivot tables, the documents of which could be found <a href="https://openpyxl.readthedocs.io/en/stable/index.html" target="_blank">here</a>.

Create row and column reference

To ensure the code continues to work with any amount of data, we need to determine the minimum and maximum active column and row of each pivot table. We must first load the workbook with load_workbook() and locate the sheet we want to work with using wb['sheet_name']. Then, we can get the data location to create charts from.

```python
wb = load_workbook(filename=wb_filename) # Load workbook
sheet = wb[sheet_name] # Locate sheet

# Get pivot table range
min_column = sheet.min_column
max_column = sheet.max_column
min_row = sheet.min_row
max_row = sheet.max_row

chart = BarChart() # Initialize bar chart
data = Reference(sheet,
                        min_col=min_column+1,
                        max_col=max_column,
                        min_row=min_row,
                        max_row=max_row) # Including headers
categories = Reference(sheet,
                        min_col=min_column,
                        max_col=min_column,
                        min_row=min_row+1,
                        max_row=max_row) # Not including headers
chart.add_data(data, titles_from_data=True) # Adding data to charts
chart.set_categories(categories)
```

The above code block would create a bar chart for the pivot table in the specified sheet.

Styling options for Excel charts
In addition to creating charts, openpyxl also provides options for styling the charts to make them more visually appealing and understandable. Here are some examples of chart styling options:

<ol>
    <li>Set chart title: Use <code>chart.title</code> attribute to set the title of the chart.</li>
    <li>Set chart legend: Use <code>chart.legend</code> attribute to set the legend position of the chart.</li>
    <li>Set chart axis labels: Use <code>chart.x_axis.title</code> and <code>chart.y_axis.title</code> attributes to set the axis labels of the chart.</li>
    <li>Set series colors: Use <code>chart.series[i].graphicalProperties.solidFill</code> attribute to set the color of the i-th series of the chart.</li>
    <li>Set chart axis scale: Use <code>chart.x_axis.scaling.min/max</code> and <code>chart.y_axis.scaling.min/max</code> attributes to set the axis scale of the chart.</li>
</ol>

These are only a few examples of the many styling options available for Excel charts in openpyxl. With openpyxl, you can customize various chart features, such as font styles, gridlines, borders, line styles, and more. However, I will only focus on a few styles in the code.

Master function for creating charts
To streamline the process of creating charts and referencing data, we can create a master function that accepts optional parameters for styling. This allows for easier creation of multiple charts with consistent data references from pivot tables. Check the function template below for an example:

```python
def create_chart(wb_filename, sheet, chart_type, style_1=None, style_2=None, ...):

        wb = load_workbook(filename=wb_filename)
        sheet = wb[sheet]
        # Get pivot table range
        min_column = sheet.min_column
        ....

        # Dictionary for initializing chart type
        CHART_DICT = {'bar': lambda: BarChart(),
                      'line': lambda: LineChart(),
                      'pie': lambda: PieChart(), ...}
        chart = CHART_DICT[chart_type]()

        # Set styles if specified
        if style_1:
                chart.style_1 = style_1
        ...
                
        data = Reference(sheet,...) # including headers
        categories = Reference(sheet,...) # not including headers
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        sheet.add_chart(chart, "A15") # Chart placement

        wb.save(wb_filename)
```

After that, we could use this function to create charts, here is an example to create a stacked bar chart:

```python
create_chart(f"Report_{today}.xlsx", sheet="YTD USA Monthly Sales",
chart_type="bar", subtype="col", grouping="stacked",
chart_title="YTD USA Monthly Sales", x_title="Month",
y_title="Sales", style=5, overlap=100)
```

# Image for YTD USA Monthly Sales

The above chart can still be improved by adjusting spacing between columns or using a different color scheme, but you got the idea of how it work. Don’t be intimidated by the styling code – take your time to explore and test each option to achieve the desired result. Testing the styling options back-and-forth can also help to fine-tune the chart and make it visually appealing.

Using crontab to automate the report
To automate the above process, we can use a tool called crontab. This tool allows us to schedule a script to run at specific intervals, such as every week at 8 AM, on Friday. We can write a script that generates charts using openpyxl, and then use crontab to run it automatically. This saves us time and ensures that our charts are always up-to-date. In this post, I would not cover the detailed steps of setting up a crontab job, but you can find a comprehensive guide <a href="https://ostechnix.com/a-beginners-guide-to-cron-jobs/" target="_blank">here</a>.

<h3>Takeaways</h3>

For the detailed code that I use in this project, check out this <a href="https://github.com/MarcusLe02/Data-Science/blob/main/excel_report_automation/excel-automation.ipynb" target="_blank">link</a>.

To summarize, creating charts in Excel using openpyxl is a valuable technique for data visualization and reporting. It provides numerous filtering & styling customization which allow you to create professional-looking charts. Additionally, creating a master function for chart creation can streamline the process and save time for repetitive tasks, making it an efficient way to create reports.

On the other hand, there are also some drawbacks to using openpyxl for report creation. One downside is the steep learning curve to understand the syntax, especially if you want to create highly customized charts. Another potential issue is the compatibility of the charts in different versions, as openpyxl may not always generate charts that are compatible with older versions of Excel. Nevertheless, with some practice and experimentation, you can achieve great results and impress your colleagues or clients with professional-looking charts.

In short, if you have a large amount of data and want to automate the Excel report generation process, openpyxl is a powerful tool that can save you time and effort in the long run.
