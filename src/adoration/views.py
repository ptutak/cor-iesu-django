from collections import namedtuple

from django.db.models import Count
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .const import DefaultValues
from .models import (
    Collection,
    CollectionConfig,
    PeriodCollection,
)


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world. You're at the polls index.")


def assignments(request: HttpRequest) -> HttpResponse:
    # collections_configs = db.session.execute(
    #     select(CollectionConfig, Collection)
    #     .join(CollectionConfig.collection)
    #     .where(Collection.enabled)
    #     .where(CollectionConfig.name == CollectionConfig.ConfigKeys.ASSIGNMENT_LIMIT)
    # ).all()
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

        class G:
            user: bool = False
            admin: bool = False

        return render(
            request,
            "adoration/assignments.html.jinja2",
            {
                "free_assignments": free_assignments,
                "available_collections": available_collections,
                "period_collections": period_collections,
                "g": G()
            },
        )

    #     g.available_collections = db.session.scalars(select(Collection).where(Collection.enabled)).all()

    #     db.session.commit()

    #     return render_template("assignments.html.jinja2")

    # form = request.form.to_dict()
    # form_fields_required = {"collection-select", "period-select", "first-name", "last-name"}
    # if not form_fields_required.issubset(form.keys()):
    #     return abort(400, f"You have to provide the following form fields: {form_fields_required}")

    # if "email" not in form and "phone-number" not in form:
    #     return abort(400, "You have to provide one of those form fields: 'email', 'phone-number'")

    # period_collection_id = int(form["period-select"])
    # collection_id = int(form["collection-select"])
    # first_name = form["first-name"]
    # last_name = form["last-name"]
    # email = None
    # phone_number = None
    # if "email" in form:
    #     email = form["email"]
    # if "phone-number" in form:
    #     phone_number = form["phone-number"]

    # period_collections = db.session.execute(
    #     select(PeriodCollection.id, func.count(PeriodAssignment.id).label("period_assignment_count"))
    #     .join(PeriodCollection.assignments, isouter=True)
    #     .where(PeriodCollection.id == period_collection_id)
    #     .group_by(PeriodCollection.id)
    # ).first()

    # if period_collections is None:
    #     return abort(400, "The period collection you have sellected is not available")

    # if period_collections.period_assignment_count < limit_per_collection.get(
    #     collection_id,
    #     g.config.get(DatabaseKeys.ASSIGNMENT_LIMIT, DefaultValues.ASSIGNMENT_LIMIT),
    # ):
    #     new_assignment = PeriodAssignment()
    #     new_assignment.id_period_collection = period_collection_id
    #     new_assignment.attendant_email = email
    #     new_assignment.attendant_phone_number = phone_number
    #     new_assignment.attendant_name = f"{first_name} {last_name}"
    #     db.session.add(new_assignment)
    # db.session.commit()

    return JsonResponse({"limit_per_collection": limit_per_collection, "free_assignments": free_assignments})
