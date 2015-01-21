from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

class IntercoolerHelperInternal():

    def __init__(self, request, template_name, intercooler_template_name, use_template_for_response):

        self.request = request
        self.template_name = template_name
        self.intercooler_template_name = intercooler_template_name
        self.response_context = dict()
        self.response_headers = dict()
        self.active_template_override = None
        self.use_template_for_response = use_template_for_response

    def is_intercooler_request(self):
        return self.request.META.get('HTTP_X_IC_REQUEST', False)

    def set_template(self, template_name):
        self.active_template_override = template_name
        self.use_template_for_response = True

    def redirect_to(self, url):
        self.response_headers['X-IC-Redirect'] = url

    def set_location(self, url):
        self.response_headers['X-IC-SetLocation'] = url

    def use_template_for_response(self, use):
        self.use_template_for_response = use

    def get_active_template(self):

        if self.active_template_override:
            return self.active_template_override
        else:
            if self.is_intercooler_request():
                active_template = self.intercooler_template_name

                # Use the default template if the other one doesnt exist
                if not active_template:
                    active_template = self.template_name
            else:
                active_template = self.template_name

        return active_template


class IntercoolerHelperView(View):

    template_name = None
    ic_template_name = None
    enable_template_for_methods = ['get']

    def get(self, request, *args, **kwargs):

        ic = IntercoolerHelperInternal(request, self.template_name, self.ic_template_name, True)
        self.on_get(ic, *args, **kwargs)
        return self.template_response(request, ic.get_active_template(), ic.response_context, ic.response_headers, ic.use_template_for_response)

    def post(self, request, *args, **kwargs):

        ic = IntercoolerHelperInternal(request, self.template_name, self.ic_template_name, False)
        self.on_post(ic, *args, **kwargs)
        return self.template_response(request, ic.get_active_template(), ic.response_context, ic.response_headers, ic.use_template_for_response)

    def put(self, request, *args, **kwargs):

        ic = IntercoolerHelperInternal(request, self.template_name, self.ic_template_name, False)
        self.on_put(ic, *args, **kwargs)
        return self.template_response(request, ic.get_active_template(), ic.response_context, ic.response_headers, ic.use_template_for_response)

    def delete(self, request, *args, **kwargs):

        ic = IntercoolerHelperInternal(request, self.template_name, self.ic_template_name, False)
        self.on_delete(ic, *args, **kwargs)
        return self.template_response(request, ic.get_active_template(), ic.response_context, ic.response_headers, ic.use_template_for_response)

    def on_get(self, context, headers, request, **kwargs):
        pass

    def on_post(self, context, headers, request, **kwargs):
        pass

    def on_put(self, context, headers, request, **kwargs):
        pass

    def on_delete(self, context, headers, request, **kwargs):
        pass

    def template_response(self, request, active_template, context, headers, use_template_for_response):

        if use_template_for_response:
            response = render(request, active_template, context)
        else:
            response = HttpResponse()

        for header in headers.keys():
            val = headers[header]
            response[header] = val

        return response