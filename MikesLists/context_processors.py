#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
r"""
context_processors.py
MikesLists.context_processors
/srv/django/MikesLists_dev/MikesLists/context_processors.py

"""
__version__ = "0.0.0.000004-dev"
__author__ = "Mike Merrett"
__updated__ = "2026-01-18 22:21:25"
###############################################################################



# MikesLists/context_processors.py
from django.conf import settings


def export_env_vars(request):

    X = getattr(settings, "ENV_NAME", "dev")
    # print(f"@@@{ X=}@@@")
    return {"env": X}


# def env_name(request):
#     """
#     Returns the environment name to all templates.
#     """
#     return {"env": getattr(settings, "ENV_NAME", "dev").lower()}





#   <span class="badge bg-primary">
# This key "env" is what you will use in your HTML: {{ env }}
# return {"env": getattr(settings, "ENV_NAME", "dev").lower()}


# <h1>Environment: {{ env }}</h1>


# def env_name(request): # Match what Django is looking for
#     return {"env": "SUCCESSCCC"}
# #     from django.conf import settings
# #     return {"env": getattr(settings, "ENV_NAME", "dev").lower()}


# <h1>Environment</h1>
# <p>X{{ env }}X</p>




# <h1 class="display-4 text-blue">EnvironmentMM:

#         {{ env|default:"NOT_FOUND_IN_CONTEXT" }}

# </h1>




    # <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm mb-4">
    #     <div class="container">
    #         <a class="navbar-brand fw-bold" href="/">🚀 MikesLists</a>
    #         <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
    #             <span class="navbar-toggler-icon"></span>
    #         </button>

    #         <div class="collapse navbar-collapse" id="navbarNav">
    #             <ul class="navbar-nav ms-auto">
    #                 {% if user.is_authenticated %}
    #                     <li class="nav-item text-light me-3">EnvironmentMu: {{ env|default:"NOT_FOUND_IN_CONTEXT" }}
    #                     </li>
    #                     <li class="nav-item">
    #                         <span class="nav-link text-light me-3">Welcome, {{ user.username }}</span>
    #                     </li>
    #                     <li class="nav-item">
    #                         <form action="{% url 'accounts:logout' %}" method="post" class="d-inline">
    #                             {% csrf_token %}
    #                             <button type="submit" class="btn btn-outline-light btn-sm">Logout</button>
    #                         </form>
    #                     </li>
    #                 {% else %}
    #                     <li class="nav-item">
    #                         <a class="nav-link" href="{% url 'accounts:login' %}">Login</a>
    #                     </li>
    #                     <li class="nav-item">
    #                         <a class="btn btn-primary btn-sm ms-lg-2" href="{% url 'accounts:register' %}">Sign Up</a>
    #                     </li>
    #                 {% endif %}
    #             </ul>
    #         </div>
    #     </div>
    # </nav>
