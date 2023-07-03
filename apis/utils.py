# ---------- Python's Libraries ---------------------------------------------------------------------------------------
import os

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.core.paginator import Paginator, InvalidPage, PageNotAnInteger, EmptyPage

# ---------- Created Tools --------------------------------------------------------------------------------------------


URL = os.environ.get('DOMAIN_NAME', 'http://localhost:3000')
# ========== PERMISSION ===============================================================================================
# ---------- Permission Level -----------------------------------------------------------------------------------------

PERMISSION_LEVEL_NONE = 0
PERMISSION_LEVEL_VIEW_ONLY = 1
PERMISSION_LEVEL_GENERAL = 2
PERMISSION_LEVEL_ADMIN = 3
CHOICE_PERMISSION_LEVEL = (
    (PERMISSION_LEVEL_NONE, "none"),
    (PERMISSION_LEVEL_VIEW_ONLY, "view only"),
    (PERMISSION_LEVEL_GENERAL, "document"),
    (PERMISSION_LEVEL_ADMIN, "admin"),
)

# ---------- Custom Field Instruction Type ----------------------------------------------------------------------------
FORMS_INSTRUCTIONS_TYPE_PASS_FAIL = 0
FORMS_INSTRUCTIONS_TYPE_TEXT_BOX = 1
FORMS_INSTRUCTIONS_TYPE_NUMBER = 2
FORMS_INSTRUCTIONS_TYPE_OPTION_LIST = 3
FORMS_INSTRUCTIONS_TYPE_DROPDOWN_LIST = 4
FORMS_INSTRUCTIONS_TYPE_FILE = 5
FORMS_INSTRUCTIONS_TYPE_PDF_FIELD = 6
CHOICE_FORM_TYPE = (
    (FORMS_INSTRUCTIONS_TYPE_PASS_FAIL, "Pass/Fail Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_TEXT_BOX, "Text Box Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_NUMBER, "Number Input Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_OPTION_LIST, "Option List Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_DROPDOWN_LIST, "Dropdown List Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_FILE, "File Input Instruction Form"),
    (FORMS_INSTRUCTIONS_TYPE_PDF_FIELD, "PDF Field Instruction Form"),
)


# ---------- Get Paginator Function -----------------------------------------------------------------------------------


def get_paginator(request, qs):
    try:
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))

    except ValueError:
        page, limit = 1, 10

    paginator = Paginator(qs, limit)

    try:
        page_object = paginator.page(page)
        object_list = page_object.object_list

    except (InvalidPage, PageNotAnInteger, EmptyPage):
        return [], None, None

    return object_list, paginator.count, page
