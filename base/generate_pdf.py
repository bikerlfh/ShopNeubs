import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string


def generate_pdf(template,context):
	rendered = render_to_string(template,context)
	options = {'margin-top': '0.10in',
			   'margin-right': '0.25in',
			   'margin-bottom': '0.25in',
			   'margin-left': '0.25in',
			   'encoding': "UTF-8",'no-outline': None,
			}
	pdf = pdfkit.from_string(rendered,False,options= options)
	return HttpResponse(pdf,content_type='application/pdf')