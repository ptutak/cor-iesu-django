from collections import namedtuple

from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect

from .const import DefaultValues
from .models import Collection, CollectionConfig, PeriodCollection, PeriodAssignment


class G:
    user: bool = False
    admin: bool = False


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")


def assignments(request: HttpRequest) -> HttpResponse:
    collections_configs = CollectionConfig.objects.filter(
        collection__enabled=True, name=CollectionConfig.ConfigKeys.ASSIGNMENT_LIMIT
    )
    limit_per_collection = {config.collection.id: int(config.value) for config in collections_configs}
    if request.method == "GET":
        period_collections = PeriodCollection.objects.filter(collection__enabled=True).annotate(
            assignments_count=Count("periodassignment")
        )
        free_assignment = namedtuple(
            "free_assignment",
            ["collection_id", "collection_name", "period_collection_id", "period_name", "occupied_places"],
        )

        free_assignments = [
            free_assignment(
                collection_id=period_collection.collection.id,
                collection_name=period_collection.collection.name,
                period_name=period_collection.period.name,
                period_collection_id=period_collection.id,
                occupied_places=period_collection.assignments_count,
            )
            for period_collection in period_collections
            if period_collection.assignments_count
            < limit_per_collection.get(period_collection.collection.id, DefaultValues.ASSIGNMENT_LIMIT)
        ]

        available_collections = Collection.objects.filter(enabled=True)

        return render(
            request,
            "adoration/assignments.html.jinja2",
            {
                "free_assignments": free_assignments,
                "available_collections": available_collections,
                "period_collections": period_collections,
                "g": G(),
            },
        )

    form = request.POST
    form_fields_required = {"collection-select", "period-select", "first-name", "last-name"}
    if not form_fields_required.issubset(form.keys()):
         return HttpResponseBadRequest(f"You have to provide the following form fields: {form_fields_required}")

    if "email" not in form and "phone-number" not in form:
        return HttpResponseBadRequest("You have to provide one of those form fields: 'email', 'phone-number'")

    period_collection_id = int(form["period-select"])
    first_name = form["first-name"]
    last_name = form["last-name"]
    email = None
    phone_number = None
    if "email" in form:
        email = form["email"]
    if "phone-number" in form:
        phone_number = str(form["phone-number"])

    period_collection = PeriodCollection.objects.filter(id=period_collection_id, collection__enabled=True).annotate(
        assignments_count=Count("periodassignment")
    ).first()

    if period_collection is None:
        return HttpResponseBadRequest("The period collection you have sellected is not available")



    if period_collection.assignments_count < limit_per_collection.get(period_collection.collection.id, DefaultValues.ASSIGNMENT_LIMIT):
        new_assignment = PeriodAssignment(
            period_collection=PeriodCollection.objects.get(id=period_collection_id),
            attendant_email=email,
            attendant_phone_number=phone_number,
            attendant_name=f"{first_name} {last_name}",
        )
        new_assignment.save()

    return redirect("assignments")
