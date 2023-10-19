from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_required, current_user

from .. import forms, db, models
from ..models import User, Property, PropertyFavourites
from datetime import datetime
import requests

properties_views = Blueprint('properties_views', __name__)


@properties_views.route("/map", methods=['GET', 'POST'])
@login_required
def map_page():
    result_list, property_list = [], []
    target_address = []
    form = forms.TargetLocationForm()
    dynamic_form = forms.DynamicForm()
    filters_form = forms.FiltersForm()
    target = [1.369635, 103.803680]  # middle of sg coords
    if form.validate_on_submit():
        target_location = form.target_location.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum=1".format(
            target_location  # 639798
        )
        response = requests.request("GET", url)
        data = response.json()
        pages = data['totalNumPages']

        for item in data['results']:
            result_list.append((item['ADDRESS'], item['ADDRESS']))
        # print(result_list)

        for i in range(2, pages + 1):
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum={}".format(
                target_location,
                i
            )
            response = requests.request("GET", url)
            data = response.json()
            for item in data['results']:
                result_list.append((item['ADDRESS'], item['ADDRESS']))

        dynamic_form.address.choices = result_list

        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,p_list = [],
                               dynamic_form=dynamic_form, filters_form = filters_form,property_list=[],
                               target=target, target_address = [])

    elif dynamic_form.validate_on_submit() and not filters_form.validate_on_submit():
        target_location = dynamic_form.address.data
        filters_form.address.choices = [target_location]
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            target_location
        )
        response = requests.request("GET", url)
        data = response.json()
        address_details = data['results'][0]
        target_address = address_details
        # print(address_details)

        # query into db for properties
        initial_property_list = Property.query_(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), [])
        # print(len(property_list))
        # print(property_list[0]['distance'])
        filtered = list(filter(lambda num: num['distance'] < 3
                               and num['monthly_rent'] < 10000,
                               initial_property_list))  #default filters, distance 0-3km, monthly_rent 0-10000sgd
        # print(len(filtered))
        # print(filtered)
        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,p_list = initial_property_list,
                               dynamic_form=dynamic_form,filters_form = filters_form, property_list=filtered,
                               target=[float(address_details['LATITUDE']), float(address_details['LONGITUDE'])],target_address = target_address)
    elif filters_form.validate_on_submit():
        target_location = filters_form.address.data
        distance = filters_form.distance.data
        monthly_rent = filters_form.monthly_rent.data
        floor_size = filters_form.floor_size.data
        num_of_bedrooms = filters_form.num_of_bedrooms.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            target_location
        )
        response = requests.request("GET", url)
        data = response.json()
        address_details = data['results'][0]
        target_address = address_details
        # print(address_details)

        # query into db for properties
        initial_property_list = Property.query_(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), [])
        # print(len(property_list))
        # print(property_list[0]['distance'])
        filtered = list(filter(lambda num: num['distance'] < distance
                               and num['monthly_rent'] < monthly_rent
                               and num['number_of_bedrooms'] > num_of_bedrooms
                               and num['floorsize'] > floor_size,
                               initial_property_list))  #default filters, distance 0-3km, monthly_rent 0-10000sgd
        


        return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,
                               dynamic_form=dynamic_form, filters_form = filters_form,property_list=filtered,
                               target=[float(address_details['LATITUDE']), float(address_details['LONGITUDE'])])

    return render_template("query_map_page.html", user=current_user, form=form, result_list=result_list,
                           dynamic_form=dynamic_form, filters_form = filters_form,property_list=property_list,
                           target=target)


@properties_views.route("/map/<int:property_id>", methods=['GET', 'POST'])
@login_required
def map_page_info(property_id=None):
    return render_template("show_properties.html", user=current_user, property_id=property_id)

