from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit

def generate_pdf(template,context):
	rendered = render_to_string(template,context)
	pdf = pdfkit.from_string(rendered,False)
	return HttpResponse(pdf,content_type='application/pdf')