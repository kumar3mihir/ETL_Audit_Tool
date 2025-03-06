# /backend/routes/ai_routes.py: Contains routes for handling AI-related tasks, such as metadata analysis and report generation.
from flask import Blueprint, request, jsonify
from config import Config
import openai
import logging
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import time

ai_routes = Blueprint('ai', __name__, url_prefix='/api/ai')

def generate_ai_prompt(schema_data):
    """Generate structured prompt for AI analysis"""
    prompt = f"""Analyze this database schema and provide metadata insights:
    
    Schema Structure:
    {str(schema_data)[:3000]}  # Truncate to stay within token limits

    Provide analysis in this format:
    1. Table Purpose: Brief description of each table's function
    2. Column Analysis: Data type validation and semantic meaning
    3. Relationships: Inferred connections between tables
    4. Data Quality: Identify potential issues or anomalies
    5. Recommendations: Optimization suggestions"""
    
    return prompt

@ai_routes.route('/analyze', methods=['POST'])
def analyze_metadata():
    """Process schema data with AI model"""
    try:
        data = request.get_json()
        schema_data = data.get('schema')
        model = data.get('model', Config.AI_MODEL)

        prompt = generate_ai_prompt(schema_data)
        
        if model == 'deepseek-r1:free':
            # Implement DeepSeek API integration
            response = "DeepSeek integration placeholder - implement API call"
        else:
            # Default to OpenAI GPT-4
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=1500
            ).choices[0].message.content

        return jsonify({
            'analysis': response,
            'model': model,
            'timestamp': int(time.time())
        }), 200

    except Exception as e:
        logging.error(f"AI analysis error: {str(e)}")
        return jsonify({'error': 'Metadata analysis failed'}), 500

@ai_routes.route('/report', methods=['POST'])
def generate_report():
    """Generate Excel/PDF report from AI analysis"""
    try:
        data = request.get_json()
        analysis = data.get('analysis')
        report_type = data.get('type', 'pdf')

        # Create structured data from AI analysis
        report_data = parse_ai_response(analysis)
        
        if report_type == 'excel':
            output = generate_excel_report(report_data)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            output = generate_pdf_report(report_data)
            mimetype = 'application/pdf'

        return output, 200, {
            'Content-Type': mimetype,
            'Content-Disposition': f'attachment; filename="metadata_report_{int(time.time())}.{report_type}"'
        }

    except Exception as e:
        logging.error(f"Report generation error: {str(e)}")
        return jsonify({'error': 'Report generation failed'}), 500

def parse_ai_response(text):
    """Convert AI response text to structured data"""
    sections = {}
    current_section = None
    for line in text.split('\n'):
        if line.strip().endswith(':'):
            current_section = line.strip()[:-1]
            sections[current_section] = []
        elif current_section and line.strip():
            sections[current_section].append(line.strip())
    return sections

def generate_excel_report(data):
    """Generate Excel report using pandas"""
    df = pd.DataFrame([
        {'Section': key, 'Content': '\n'.join(value)}
        for key, value in data.items()
    ])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Metadata Analysis')
    output.seek(0)
    return output.getvalue()

def generate_pdf_report(data):
    """Generate PDF report using ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("AI Metadata Analysis Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    for section, content in data.items():
        story.append(Paragraph(section, styles['Heading2']))
        for item in content:
            story.append(Paragraph(f"• {item}", styles['BodyText']))
        story.append(Spacer(1, 8))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

@ai_routes.route('/models')
def list_models():
    """Return available AI models"""
    return jsonify({
        'models': ['gpt-4', 'deepseek-r1:free'],
        'default': Config.AI_MODEL
    }), 200








'''Sure, I'll add comments to the code to explain it in detail and then summarize its purpose and usage.

Detailed Comments
Purpose and Usage
This code defines a Flask Blueprint for handling AI-related routes. It provides endpoints to analyze database schema metadata using AI models and generate reports based on the analysis. Here's a summary of its purpose and usage:

Endpoints:

/api/ai/analyze: Accepts a POST request with schema data and an optional AI model. It generates a prompt for the AI model to analyze the schema and returns the analysis.
/api/ai/report: Accepts a POST request with AI analysis data and a report type (PDF or Excel). It generates and returns the report.
/api/ai/models: Returns a list of available AI models and the default model.
Functions:

generate_ai_prompt(schema_data): Creates a structured prompt for AI analysis based on the provided schema data.
//my view -- think how much schema it fetched based on it -- we calculate the token and price -- if its more than threshold then we will process it in chunks
parse_ai_response(text): Parses the AI response text into structured data.
generate_excel_report(data): Generates an Excel report from the structured data using pandas.
generate_pdf_report(data): Generates a PDF report from the structured data using ReportLab.
How to Use
Setup:

Ensure you have Flask, pandas, openai, and reportlab installed.
Configure your AI model settings in the Config class.
Run the Flask Application:

Register the ai_routes Blueprint with your Flask app.
Start the Flask server.
Make Requests:

Send a POST request to /api/ai/analyze with schema data to get AI analysis.
Send a POST request to /api/ai/report with AI analysis data to generate a report.
Send a GET request to /api/ai/models to get the list of available AI models.
This setup allows you to leverage AI for analyzing database schemas and generating insightful reports in different formats.

Summary'''