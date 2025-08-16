{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica-Bold;\f1\fswiss\fcharset0 Helvetica;\f2\fnil\fcharset0 .SFNS-Regular;
\f3\froman\fcharset0 TimesNewRomanPSMT;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl250\slmult1\pardirnatural\partightenfactor0

\f0\b\fs33\fsmilli16940 \cf2 User Story
\f1\b0\fs26\fsmilli13090 \
\
\pard\tx860\tx1420\tx1980\tx2540\tx3100\tx3660\tx4220\tx4780\tx5340\tx5900\tx6460\tx7020\li300\sl250\slmult1\partightenfactor0

\f0\b \cf2 As a
\f1\b0  business intelligence analyst at an e-commerce company,\

\f0\b I want
\f1\b0  to access clean, well-structured sales, customer, and product data in a single warehouse,\

\f0\b so that
\f1\b0  I can quickly generate reports and uncover trends without manually cleaning or joining multiple raw data files.\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\fs18\fsmilli9240 \cf2 \

\f2 \uc0\u11835 
\f1 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl250\slmult1\pardirnatural\partightenfactor0

\fs26\fsmilli13090 \cf2 \

\f0\b\fs33\fsmilli16940 Problem Statement
\f1\b0\fs26\fsmilli13090 \
\
The company\'92s sales, customer, and product data is scattered across multiple raw CSV files, each with inconsistent formats, missing values, and duplicate entries. This fragmentation makes it time-consuming for analysts to create accurate reports, delays decision-making, and increases the risk of errors in business insights. There is no centralized, analytics-ready dataset to support performance tracking, customer segmentation, or product sales analysis.\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\fs18\fsmilli9240 \cf2 \

\f2 \uc0\u11835 
\f1 \
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl250\slmult1\pardirnatural\partightenfactor0

\fs26\fsmilli13090 \cf2 \

\f0\b\fs33\fsmilli16940 Use Case
\f1\b0\fs26\fsmilli13090 \
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl250\slmult1\pardirnatural\partightenfactor0

\f0\b \cf2 Title:
\f1\b0  Building an analytics-ready e-commerce data warehouse\
\

\f0\b Actors:
\f1\b0 \
\pard\tqr\tx100\tx260\li260\fi-260\sl250\slmult1\sb240\partightenfactor0
\cf2 	\'95	Data Engineering Team (responsible for ingestion, transformation, and loading)\
	\'95	Business Intelligence Analysts (consumers of cleaned data)\
	\'95	Management Team (decision-makers using insights)\
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\sl250\slmult1\pardirnatural\partightenfactor0

\f0\b \cf2 Scenario:
\f1\b0 \
\pard\tqr\tx300\tx460\li460\fi-460\sl250\slmult1\sb240\partightenfactor0

\f3 \cf2 	1.	Data engineers ingest raw sales, customer, product, seller, and payment data from multiple CSV sources.\
	2.	They design and implement a 
\f0\b star schema
\f1\b0  in a central data warehouse.\

\f3 	3.	ETL/ELT pipelines populate 
\f0\b dimension tables
\f1\b0  (customers, products, sellers, dates) and a 
\f0\b fact table
\f1\b0  (sales).\

\f3 	4.	Data quality checks ensure referential integrity, remove duplicates, and validate numerical ranges.\
	5.	Analysts query the warehouse to:\
\pard\tqr\tx500\tx660\li660\fi-660\sl250\slmult1\sb240\partightenfactor0
\cf2 	\'95	Track monthly sales trends.\
	\'95	Identify top-performing products and sellers.\
	\'95	Segment customers based on purchase behavior.\
\pard\tqr\tx300\tx460\li460\fi-460\sl250\slmult1\sb240\partightenfactor0
\cf2 	6.	Management uses these insights to guide marketing spend, inventory planning, and seller partnerships.}